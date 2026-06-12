"""x86-64 NASM assembly generator from IR quadruples."""


from ir_generator import IROperand

# Fallback element count when array size cannot be determined statically.
_FALLBACK_ARRAY_ELEMS = 4


class AssemblyGenerator:
    """Consumes IR quadruples and emits NASM x86-64 assembly.

    Uses a simple two-pass strategy:
      Pass 1 — collect all variable/temp names to allocate stack offsets.
      Pass 2 — walk quads again and emit instructions.
    """

    def __init__(self, quads):
        self.quads = quads
        self.lines = []
        self.offsets = {}       # name -> negative offset from rbp
        self.stack_used = 0
        self.current_fn = None
        self._pending_args = []  # args collected before a call
        self._param_idx = 0     # index of current param being processed

    # ---- helpers ----

    def _is_label(self, name):
        if isinstance(name, IROperand):
            return name.is_label
        return name is None or name == "_" or (isinstance(name, str) and name.startswith("L"))

    def _is_num(self, s):
        if isinstance(s, IROperand):
            return s.is_const
        try:
            int(s)
            return True
        except (ValueError, TypeError):
            return False

    def _alloc(self, op, elem_count=1):
        """Reserve *elem_count* x 8 bytes on the stack for *op*.

        For a scalar (``elem_count == 1``) the single slot is at the
        current stack bottom.  For an array the *base* (``a[0]``) is
        placed at the *top* of the N‑slot block so that ``a[k]``
        resides at ``base - k·8`` — the block grows downward from
        the base and stays within the reserved stack space.
        """
        if op is None:
            return
        if isinstance(op, IROperand):
            if op.is_label or op.is_const:
                return
            key = op.value
        else:
            if self._is_label(op) or self._is_num(op):
                return
            key = op
        if key not in self.offsets:
            n = max(1, elem_count)
            self.stack_used += n * 8
            if n > 1:
                # Array: base sits atop the N‑slot block.
                self.offsets[key] = -(self.stack_used - (n - 1) * 8)
            else:
                self.offsets[key] = -self.stack_used

    def _op(self, opnd):
        """Convert an IR operand (``IROperand`` or plain string) into a
        NASM operand — either a numeric constant, a label name, or
        ``[rbp+offset]`` for stack-allocated variables/temps."""
        if opnd is None:
            return None
        if isinstance(opnd, IROperand):
            if opnd.is_label:
                return opnd.value
            if opnd.is_const:
                return opnd.value
            off = self.offsets.get(opnd.value)
            if off is not None:
                return f"[rbp{off}]"
            return opnd.value
        if opnd == "_":
            return None
        if self._is_label(opnd):
            return opnd
        if self._is_num(opnd):
            return opnd
        off = self.offsets.get(opnd)
        if off is not None:
            return f"[rbp{off}]"
        return opnd

    def _emit(self, text, indent=True):
        if indent and text:
            self.lines.append("    " + text)
        else:
            self.lines.append(text if text else "")

    def _raw_offset(self, opnd):
        """Return the raw numeric offset of *opnd*, or ``None``.

        Unlike ``_op()`` which returns ``[rbp-24]``, this returns
        ``-24`` so callers can do arithmetic on the offset itself.
        """
        if opnd is None:
            return None
        if isinstance(opnd, IROperand):
            key = opnd.value
        else:
            key = str(opnd)
        off = self.offsets.get(key)
        if off is None:
            return None
        return off

    # ---- main entry ----

    def generate(self):
        # Pass 0a: scan for array element counts from ``param`` type info
        array_counts = self._scan_array_sizes()

        # Pass 0b: also flag names used as local array bases (no param type).
        # Without this they'd be allocated as 1-element scalars and array
        # slots would overlap with subsequent variables.
        for q in self.quads:
            if q.op in ("array_set", "array_get") and q.arg1 is not None:
                key = q.arg1.value if isinstance(q.arg1, IROperand) else str(q.arg1)
                if key not in array_counts:
                    array_counts[key] = _FALLBACK_ARRAY_ELEMS

        # Pass 1: collect stack vars, using element counts for arrays
        for q in self.quads:
            for a in (q.arg1, q.arg2, q.result):
                if a is None:
                    continue
                if isinstance(a, IROperand):
                    key = a.value
                else:
                    if self._is_label(a) or self._is_num(a):
                        continue
                    key = a
                cnt = array_counts.get(key, 1)
                self._alloc(a, cnt)

        # Pass 2: emit
        self._emit("default rel", indent=False)
        self._emit("global main", indent=False)
        self._emit("", indent=False)
        self._emit("section .text", indent=False)
        for q in self.quads:
            self._emit_quad(q)
        return "\n".join(self.lines)

    def _scan_array_sizes(self):
        """Extract array-element counts from ``receive_param`` type info.

        Returns ``{name: element_count}``.
        """
        counts = {}
        for q in self.quads:
            if q.op == "receive_param" and q.result is not None:
                raw = str(q.result)
                if raw.startswith("[") and ";" in raw:
                    parts = raw.split(";", 1)
                    cnt = parts[1].rstrip("]")
                    if cnt.isdigit():
                        counts[str(q.arg1)] = int(cnt)
        return counts

    # ---- quad handlers ----

    def _emit_quad(self, q):
        op = q.op
        if op == "func":
            self.current_fn = q.arg1
            self._param_idx = 0
            self._emit(f"{q.arg1}:", indent=False)
            self._emit("push rbp")
            self._emit("mov rbp, rsp")
            if self.stack_used > 0:
                self._emit(f"sub rsp, {self.stack_used}")

        elif op == "receive_param":
            regs = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
            dst = self._op(q.arg1)
            if dst and self._param_idx < len(regs):
                self._emit(f"mov {dst}, {regs[self._param_idx]}")
            self._param_idx += 1

        elif op == "endfunc":
            self._emit(f"ret_{self.current_fn}:", indent=False)
            self._emit("mov rsp, rbp")
            self._emit("pop rbp")
            self._emit("ret")
            self._emit("", indent=False)

        elif op == "alloc":
            # Variable slot reservation; no assembly emitted here, the
            # front-end allocates the stack frame based on the parsed AST.
            pass

        elif op == "array_lit":
            # Lowered to individual ``array_set`` quads in the IR generator.
            pass

        elif op == "array_get":
            # (array_get, arr, idx, result)   →  load arr[idx]
            base_off = self._raw_offset(q.arg1)
            if base_off is None:
                return
            idx_val = self._op(q.arg2)
            dst_val = self._op(q.result)
            if dst_val is None:
                return
            if self._is_num(idx_val):
                idx = int(str(idx_val))
                # Array elements grow downward: a[k] at base_off - k*8
                self._emit(f"mov rax, [rbp{base_off - idx * 8}]")
            else:
                self._emit(f"mov rcx, {idx_val}")
                self._emit("neg rcx")
                self._emit(f"mov rax, [rbp{base_off} + rcx*8]")
            self._emit(f"mov {dst_val}, rax")

        elif op == "array_set":
            # (array_set, arr, idx, val)   →  store arr[idx] = val
            base_off = self._raw_offset(q.arg1)
            if base_off is None:
                return
            idx_val = self._op(q.arg2)
            val_op = self._op(q.result)
            if val_op is None:
                return
            if self._is_num(idx_val):
                idx = int(str(idx_val))
                self._emit(f"mov rax, {val_op}")
                self._emit(f"mov [rbp{base_off - idx * 8}], rax")
            else:
                self._emit(f"mov rcx, {idx_val}")
                self._emit("neg rcx")
                self._emit(f"mov rax, {val_op}")
                self._emit(f"mov [rbp{base_off} + rcx*8], rax")

        elif op == "=":
            dst = self._op(q.result)
            src = self._op(q.arg1)
            if dst and src is not None:
                self._emit(f"mov rax, {src}")
                self._emit(f"mov {dst}, rax")

        elif op == "assign":
            src = self._op(q.arg1)
            dst = self._op(q.result)
            if dst and src is not None:
                self._emit(f"mov rax, {src}")
                self._emit(f"mov {dst}, rax")

        elif op == "return_val":
            if q.arg1 is not None:
                src = self._op(q.arg1)
                self._emit(f"mov rax, {src}")
            self._emit(f"jmp ret_{self.current_fn}")

        elif op == "return_void":
            self._emit(f"jmp ret_{self.current_fn}")

        # Binary arithmetic
        elif op in ("+", "-", "*", "/"):
            left = self._op(q.arg1)
            right = self._op(q.arg2)
            dst = self._op(q.result)
            self._emit(f"mov rax, {left}")
            if op == "+":
                self._emit(f"add rax, {right}")
            elif op == "-":
                self._emit(f"sub rax, {right}")
            elif op == "*":
                self._emit(f"imul rax, {right}")
            elif op == "/":
                self._emit("cqo")
                # idiv 需要 qword 关键字来指定操作数大小（NASM 内存操作数要求）
                if right.startswith("[") and right.endswith("]"):
                    self._emit(f"idiv qword {right}")
                else:
                    self._emit(f"idiv {right}")
            self._emit(f"mov {dst}, rax")

        # Comparison
        elif op in ("<", "<=", ">", ">=", "==", "!="):
            left = self._op(q.arg1)
            right = self._op(q.arg2)
            dst = self._op(q.result)
            cmap = {"<": "setl", "<=": "setle", ">": "setg",
                    ">=": "setge", "==": "sete", "!=": "setne"}
            self._emit(f"mov rax, {left}")
            self._emit(f"cmp rax, {right}")
            self._emit(f"{cmap[op]} al")
            self._emit("movzx rax, al")
            self._emit(f"mov {dst}, rax")

        # Control flow
        elif op == "if_false":
            cond = self._op(q.arg1)
            self._emit(f"mov rax, {cond}")
            self._emit("cmp rax, 0")
            self._emit(f"je {q.result}")

        elif op == "goto":
            self._emit(f"jmp {q.result}")

        elif op == "label":
            self._emit(f"{q.result}:", indent=False)

        # Unary minus
        elif op == "neg":
            src = self._op(q.arg1)
            dst = self._op(q.result)
            self._emit(f"mov rax, {src}")
            self._emit("neg rax")
            self._emit(f"mov {dst}, rax")

        # Function call
        elif op == "push_arg":
            self._pending_args.append(q.arg1)

        elif op == "call":
            n = int(q.arg2.value) if q.arg2 else 0
            args = self._pending_args[-n:] if n > 0 else []
            self._pending_args = []
            # System V AMD64 ABI: rdi, rsi, rdx, rcx, r8, r9
            regs = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
            for i, a in enumerate(args):
                if i < len(regs):
                    self._emit(f"mov {regs[i]}, {self._op(a)}")
            self._emit("sub rsp, 8  ; align stack")
            self._emit(f"call {q.arg1}")
            self._emit("add rsp, 8")
            dst = self._op(q.result)
            if dst:
                self._emit(f"mov {dst}, rax")
