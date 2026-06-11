"""Three-address code (quadruple) IR generator from AST.

The IR is a list of :class:`Quadruple` records ``(op, arg1, arg2, result)``.

Supported operations
--------------------

Arithmetic: ``+  -  *  /``        — i32 binary ops
Comparison: ``<  <=  >  >=  ==  !=`` — return i32 (0/1)
Logical:    ``&&  ||  !``          — i32 logical ops
Control:    ``if_false``, ``goto``, ``label``
Functions:  ``func``, ``param``, ``arg``, ``call``, ``return``, ``endfunc``
Data:       ``=`` (constant / copy), ``assign`` (variable assignment),
            ``alloc`` (variable slot reservation), ``array_get``,
            ``array_set``, ``array_lit``.
"""

from __future__ import annotations

from typing import List, Optional

from compiler_ast import *


# --------------------------------------------------------------------------- #
# IROperand — typed operand carrying a kind tag                                #
# --------------------------------------------------------------------------- #

class IROperand:
    """A typed operand in the intermediate representation.

    Each operand carries a *value* and a *kind* tag that tells the backend
    what the value represents (a temporary, a label, a constant, a variable,
    …) so it can handle each kind without string-shape heuristics.
    """
    __slots__ = ("value", "kind")

    def __init__(self, value, kind: str = "var"):
        self.value = str(value) if value is not None else "_"
        self.kind = kind          # "var" | "temp" | "label" | "const" | "func"

    # -- query helpers (used by the asm backend) --

    @property
    def is_temp(self) -> bool:
        return self.kind == "temp"

    @property
    def is_label(self) -> bool:
        return self.kind == "label"

    @property
    def is_const(self) -> bool:
        return self.kind == "const"

    # -- display / serialisation --

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"<{self.kind}:{self.value}>"

    def to_dict(self):
        return {"value": self.value, "kind": self.kind}


# --------------------------------------------------------------------------- #
# Quadruple — single IR instruction                                           #
# --------------------------------------------------------------------------- #

class Quadruple:
    """A single IR instruction: ``(op, arg1, arg2, result)``.

    Every operand slot is stored as an :class:`IROperand` (or ``None``).
    Raw strings, integers, etc. are automatically *lifted* into
    ``IROperand`` on construction so callers can keep writing
    ``_emit("+", "x", 1, t)`` without explicit wrapping.
    """
    __slots__ = ("op", "arg1", "arg2", "result")

    def __init__(self, op: str, arg1=None, arg2=None, result=None):
        self.op = op
        self.arg1 = self._lift(arg1)
        self.arg2 = self._lift(arg2)
        self.result = self._lift(result)

    @staticmethod
    def _lift(val):
        """Coerce a raw value into an :class:`IROperand` when needed."""
        if val is None or isinstance(val, IROperand):
            return val
        if isinstance(val, (int, float)):
            return IROperand(str(int(val)), kind="const")
        if isinstance(val, str):
            # Infer kind from the string shape so most call sites don't
            # have to construct ``IROperand`` explicitly.
            if val.startswith("t") and len(val) > 1 and val[1:].isdigit():
                return IROperand(val, kind="temp")
            if val.startswith("L"):
                return IROperand(val, kind="label")
            if val.lstrip("-").isdigit():
                return IROperand(val, kind="const")
            return IROperand(val, kind="var")
        raise TypeError(f"Cannot lift {type(val).__name__} to IROperand")

    def __str__(self):
        def fmt(x):
            return "_" if x is None else str(x)
        return f"({self.op}, {fmt(self.arg1)}, {fmt(self.arg2)}, {fmt(self.result)})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """JSON-safe dict — returns plain strings so the front-end
        sees exactly the same shape as before."""
        return {
            "op": self.op,
            "arg1": str(self.arg1) if self.arg1 is not None else None,
            "arg2": str(self.arg2) if self.arg2 is not None else None,
            "result": str(self.result) if self.result is not None else None,
        }


# --------------------------------------------------------------------------- #
# IR Generator                                                                 #
# --------------------------------------------------------------------------- #

class IRGenerator:
    """Walks the AST and emits three-address code quadruples."""

    def __init__(self):
        self.quads: List[Quadruple] = []
        self._temp_counter: int = 0
        self._label_counter: int = 0
        self._var_slots: dict[str, str] = {}   # AST-name -> canonical slot
        # e.g. "x" -> "x", but for arrays "a" -> "a[8]" etc.
        self._current_fn: Optional[str] = None
        self._fn_table: dict[str, FunctionDeclNode] = {}
        # Stacks for break/continue label targets.
        # _loop_exit_labels  — where ``break`` jumps  (innermost is top)
        # _loop_repeat_labels — where ``continue`` jumps (innermost is top)
        self._loop_exit_labels: List[IROperand] = []
        self._loop_repeat_labels: List[IROperand] = []

    # ---- public API ----

    def generate(self, program: ProgramNode) -> List[Quadruple]:
        self.quads = []
        self._temp_counter = 0
        self._label_counter = 0
        self._var_slots = {}
        self._fn_table = {}
        self._loop_exit_labels = []
        self._loop_repeat_labels = []
        if not isinstance(program, ProgramNode):
            return self.quads
        # Pre-collect function declarations so the expression visitor can
        # tell whether a FuncCall refers to a void function.
        for decl in program.declarations:
            if isinstance(decl, FunctionDeclNode):
                self._fn_table[decl.name] = decl
        # Program entry / exit markers bracket every translation unit.
        self._emit("program")
        for decl in program.declarations:
            if isinstance(decl, FunctionDeclNode):
                self._fn(decl)
        self._emit("endprogram")
        return self.quads

    # ---- helpers ----

    def _temp(self) -> IROperand:
        self._temp_counter += 1
        return IROperand(f"t{self._temp_counter - 1}", kind="temp")

    def _label(self, hint: str = "L") -> IROperand:
        self._label_counter += 1
        return IROperand(f"{hint}{self._label_counter - 1}", kind="label")

    def _emit(self, op: str, a1=None, a2=None, r=None) -> Quadruple:
        q = Quadruple(op, a1, a2, r)
        self.quads.append(q)
        return q

    # ---- declarations ----

    def _fn(self, node: FunctionDeclNode) -> None:
        self._current_fn = node.name
        self._emit("func", node.name)
        # Parameter slots — we lower to local copies.
        for p in node.params:
            self._emit("param", p.name, type_of(p.param_type))
        if node.body is not None:
            self._blk(node.body)
        # Ensure the function has a return epilogue even if user code
        # didn't end with a return (avoids fall-through).
        self._emit("endfunc", node.name)
        self._current_fn = None

    def _blk(self, node: BlockStmtNode) -> None:
        for s in node.statements:
            self._stmt(s)

    # ---- statements ----

    def _stmt(self, node) -> None:
        if isinstance(node, EmptyStmtNode):
            return
        if isinstance(node, BlockStmtNode):
            self._blk(node)
            return
        if isinstance(node, VarDeclStmtNode):
            self._var_decl(node)
            return
        if isinstance(node, AssignStmtNode):
            self._assign(node)
            return
        if isinstance(node, ReturnStmtNode):
            self._return(node)
            return
        if isinstance(node, BreakStmtNode):
            self._break_stmt(node)
            return
        if isinstance(node, ContinueStmtNode):
            self._continue_stmt(node)
            return
        if isinstance(node, IfStmtNode):
            self._if(node)
            return
        if isinstance(node, WhileStmtNode):
            self._while(node)
            return
        if isinstance(node, ForStmtNode):
            self._for(node)
            return
        if isinstance(node, LoopStmtNode):
            self._loop(node)
            return
        if isinstance(node, ExprStmtNode):
            # The parser sometimes wraps an assignment in an ExprStmtNode
            # (e.g. `try_parse_expression` returns AssignStmtNode and
            # `parse_statement` wraps it). Unwrap and dispatch.
            inner = node.expr
            if isinstance(inner, AssignStmtNode):
                self._assign(inner)
                return
            if isinstance(inner, FuncCallNode):
                self._call_stmt(inner)
                return
            # Plain expression — evaluate for side-effects.
            self._expr(inner)
            return
        # Unknown — be defensive: walk children.
        for attr in ("condition", "body", "then_block", "else_block",
                     "expr", "value", "left", "right", "start", "end",
                     "init_expr", "iterable"):
            child = getattr(node, attr, None)
            if isinstance(child, ASTNode):
                if attr in ("condition", "left", "right", "start", "end",
                            "index", "expr", "value", "init_expr", "iterable"):
                    self._expr(child)
                else:
                    self._stmt(child)

    def _var_decl(self, node: VarDeclStmtNode) -> None:
        # `let x: i32;`              →  (no quad — slot reserved on first use)
        # `let x: i32 = 10;`         →  (assign, 10, _, x)              ← 一行
        # `let x: i32 = a + b;`      →  (+, a, b, tN)
        #                               (assign, tN, _, x)
        # No `alloc` is emitted: the variable's type comes from the let
        # binding (known to the back-end from the symbol table), and a
        # bare declaration needs no IR — the slot is allocated lazily on
        # first assignment. Constant initializers collapse to one quad.
        if node.init_expr is None:
            return

        if isinstance(node.init_expr, NumberLiteralNode):
            # Constant initialization: one `assign` quad, no temp.
            self._emit("assign", str(node.init_expr.value), None, node.name)
            return

        # General expression initializer — fold the value into a temp,
        # then assign it to the variable's slot.
        val = self._expr(node.init_expr)
        self._emit("assign", val, None, node.name)

    def _assign(self, node: AssignStmtNode) -> None:
        # target must be an l-value (parser guarantees that)
        target = self._lvalue_target(node.left)
        val = self._expr(node.value)
        if target["kind"] == "var":
            self._emit("assign", val, None, target["name"])
        elif target["kind"] == "array_elem":
            self._emit("array_set", target["array"], target["index"], val)

    def _return(self, node: ReturnStmtNode) -> None:
        if node.expr is not None:
            val = self._expr(node.expr)
            self._emit("return", val, None, self._current_fn)
        else:
            self._emit("return", None, None, self._current_fn)

    def _break_stmt(self, node: BreakStmtNode) -> None:
        if not self._loop_exit_labels:
            # Semantic analysis should have caught this.
            return
        self._emit("goto", None, None, self._loop_exit_labels[-1])

    def _continue_stmt(self, node: ContinueStmtNode) -> None:
        if not self._loop_repeat_labels:
            return
        self._emit("goto", None, None, self._loop_repeat_labels[-1])

    def _if(self, node: IfStmtNode) -> None:
        cond = self._expr(node.condition)
        else_lab = self._label("L_else_")
        end_lab  = self._label("L_end_")
        self._emit("if_false", cond, None, else_lab)
        self._blk(node.then_block)
        self._emit("goto", None, None, end_lab)
        self._emit("label", None, None, else_lab)
        if node.else_block is not None:
            if isinstance(node.else_block, IfStmtNode):
                self._if(node.else_block)
            elif isinstance(node.else_block, BlockStmtNode):
                self._blk(node.else_block)
            else:
                self._stmt(node.else_block)
        self._emit("label", None, None, end_lab)

    def _while(self, node: WhileStmtNode) -> None:
        start = self._label("L_while_")
        end   = self._label("L_end_")
        self._loop_exit_labels.append(end)
        self._loop_repeat_labels.append(start)   # continue → re-check condition
        self._emit("label", None, None, start)
        cond = self._expr(node.condition)
        self._emit("if_false", cond, None, end)
        self._blk(node.body)
        self._emit("goto", None, None, start)
        self._emit("label", None, None, end)
        self._loop_repeat_labels.pop()
        self._loop_exit_labels.pop()

    def _for(self, node: ForStmtNode) -> None:
        """for x in a..b { body }
        IR:
            x = a
            L_for: t = x < b
                   if_false t goto L_end
                   body
            L_inc: x = x + 1        ← continue jumps here
                   goto L_for
            L_end:                   ← break jumps here
        """
        if isinstance(node.iterable, RangeNode):
            start_val = self._expr(node.iterable.start)
            end_val   = self._expr(node.iterable.end)
            self._emit("assign", start_val, None, node.var_name)
            loop_start = self._label("L_for_")
            loop_inc   = self._label("L_inc_")
            loop_end   = self._label("L_end_")
            self._loop_exit_labels.append(loop_end)
            self._loop_repeat_labels.append(loop_inc)
            self._emit("label", None, None, loop_start)
            t = self._temp()
            self._emit("<", node.var_name, end_val, t)
            self._emit("if_false", t, None, loop_end)
            self._blk(node.body)
            self._emit("label", None, None, loop_inc)
            t2 = self._temp()
            self._emit("+", node.var_name, "1", t2)
            self._emit("assign", t2, None, node.var_name)
            self._emit("goto", None, None, loop_start)
            self._emit("label", None, None, loop_end)
            self._loop_repeat_labels.pop()
            self._loop_exit_labels.pop()
        else:
            # Plain expression iterable (e.g. an array) — degenerate path.
            self._expr(node.iterable)
            self._blk(node.body)

    def _loop(self, node: LoopStmtNode) -> None:
        """loop { body }

        Aforever-loops the body.  The only way out is a ``break``
        statement inside the body (or its children).
        IR:
            L_start:  body ...
                      goto L_start
            L_end:                             ← break jumps here
        """
        start = self._label("L_loop_")
        end   = self._label("L_end_")
        self._loop_exit_labels.append(end)
        self._loop_repeat_labels.append(start)
        self._emit("label", None, None, start)
        self._blk(node.body)
        self._emit("goto", None, None, start)
        self._emit("label", None, None, end)
        self._loop_repeat_labels.pop()
        self._loop_exit_labels.pop()

    # ---- lvalue helpers ----

    def _lvalue_target(self, node) -> dict:
        """Return a description of an l-value suitable for assignment."""
        if isinstance(node, LValueNode):
            return {"kind": "var", "name": node.name}
        if isinstance(node, ArrayAccessNode):
            idx = self._expr(node.index)
            inner = node.array
            if isinstance(inner, LValueNode):
                return {"kind": "array_elem", "array": inner.name, "index": idx}
            # Nested access — materialise the inner address into a temp.
            base = self._expr(inner)
            t = self._temp()
            self._emit("=", base, None, t)
            return {"kind": "array_elem", "array": t, "index": idx}
        # Fallback: emit as expression
        return {"kind": "var", "name": self._expr(node)}

    # ---- expressions ----

    def _expr(self, node) -> IROperand:
        """Evaluate an expression and return an :class:`IROperand`
        holding its value.

        Number literals are returned as a *const* operand so that
        downstream operators can fold them in directly (e.g.
        ``(+, x, 20, t)`` instead of ``(=, 20, _, t1); (+, x, t1, t2)``).
        """
        if node is None:
            return self._temp()  # unreachable for well-formed AST
        if isinstance(node, NumberLiteralNode):
            return IROperand(str(node.value), kind="const")
        if isinstance(node, LValueNode):
            return IROperand(node.name, kind="var")
        if isinstance(node, UnaryMinusNode):
            v = self._expr(node.expr)
            t = self._temp()
            self._emit("neg", v, None, t)
            return t
        if isinstance(node, BinaryExprNode):
            left  = self._expr(node.left)
            right = self._expr(node.right)
            t = self._temp()
            self._emit(node.op, left, right, t)
            return t
        if isinstance(node, FuncCallNode):
            # Look up whether the function actually returns a value.
            decl = self._fn_table.get(node.name)
            is_void = decl is not None and decl.return_type is None
            for a in node.args:
                v = self._expr(a)
                self._emit("arg", v, None, None)
            if is_void:
                # Used as a value but the function has no return — emit
                # the call for side-effects but no result temp.
                self._emit("call", node.name, str(len(node.args)), None)
                t = self._temp()
                self._emit("=", "0", None, t)
                return t
            t = self._temp()
            self._emit("call", node.name, str(len(node.args)), t)
            return t
        if isinstance(node, ArrayLiteralNode):
            # Build the array in a synthetic temp: emit a sequence of writes
            # to fresh slots? For simplicity we emit an "array_lit" pseudo-op
            # carrying element names; the back-end can lower to allocation
            # + per-index stores.
            elem_names = [self._expr(e) for e in node.elements]
            t = self._temp()
            self._emit("array_lit", ",".join(elem_names), str(len(elem_names)), t)
            return t
        if isinstance(node, ArrayAccessNode):
            base = self._expr(node.array)
            idx  = self._expr(node.index)
            t = self._temp()
            self._emit("array_get", base, idx, t)
            return t
        if isinstance(node, RangeNode):
            # Range is not a value expression; return a placeholder
            t = self._temp()
            self._emit("=", "0", None, t)
            return t
        # Fallback
        t = self._temp()
        self._emit("=", "0", None, t)
        return t

    def _call_stmt(self, node: FuncCallNode) -> None:
        """Emit a function call that is used as a statement (no result)."""
        for a in node.args:
            v = self._expr(a)
            self._emit("arg", v, None, None)
        self._emit("call", node.name, str(len(node.args)), None)


# --------------------------------------------------------------------------- #
# Local helper — replicate the type-name logic from the semantic module       #
# so that IR generation does not depend on it.                                #
# --------------------------------------------------------------------------- #

def type_of(node) -> Optional[str]:
    """Mirror of semantic.type_of_type_node without importing semantic."""
    if node is None:
        return None
    if isinstance(node, ArrayTypeNode):
        inner = type_of(node.element_type)
        return f"[{inner};{node.size}]"
    if isinstance(node, TypeNode):
        return node.type_name
    return None
