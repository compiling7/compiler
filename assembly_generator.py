"""x86-64 NASM assembly generator from IR quadruples."""


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
        return name is None or name == "_" or (isinstance(name, str) and name.startswith("L"))

    def _is_num(self, s):
        try:
            int(s)
            return True
        except (ValueError, TypeError):
            return False

    def _alloc(self, name):
        if name is None or self._is_label(name) or self._is_num(name):
            return
        if name not in self.offsets:
            self.stack_used += 8
            self.offsets[name] = -self.stack_used

    def _op(self, name):
        """Convert name -> NASM operand (constant or [rbp+offset])."""
        if name is None or name == "_":
            return None
        if self._is_label(name):
            return name
        if self._is_num(name):
            return name
        off = self.offsets.get(name)
        if off is not None:
            return f"[rbp{off}]"
        return name  # fallback (e.g. function name for call)

    def _emit(self, text, indent=True):
        if indent and text:
            self.lines.append("    " + text)
        else:
            self.lines.append(text if text else "")

    # ---- main entry ----

    def generate(self):
        # Pass 1: collect stack vars
        for q in self.quads:
            for a in (q.arg1, q.arg2, q.result):
                self._alloc(a)

        # Pass 2: emit
        self._emit("default rel", indent=False)
        self._emit("global main", indent=False)
        self._emit("", indent=False)
        self._emit("section .text", indent=False)
        for q in self.quads:
            self._emit_quad(q)
        return "\n".join(self.lines)

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

        elif op == "param":
            regs = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
            dst = self._op(q.arg1)
            if dst and self._param_idx < len(regs):
                self._emit(f"mov {dst}, {regs[self._param_idx]}")
            self._param_idx += 1

        elif op == "endfunc":
            self._emit(f".ret_{self.current_fn}:", indent=False)
            self._emit("mov rsp, rbp")
            self._emit("pop rbp")
            self._emit("ret")
            self._emit("", indent=False)

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

        elif op == "return":
            if q.arg1 is not None:
                src = self._op(q.arg1)
                self._emit(f"mov rax, {src}")
            self._emit(f"jmp .ret_{self.current_fn}")

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
        elif op == "arg":
            self._pending_args.append(q.arg1)

        elif op == "call":
            n = int(q.arg2) if q.arg2 else 0
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
