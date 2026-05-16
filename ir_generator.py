"""Three-address code (quadruple) IR generator from AST."""

from ast import *


class Quadruple:
    """IR instruction: (op, arg1, arg2, result)."""
    def __init__(self, op, arg1=None, arg2=None, result=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result

    def __str__(self):
        return f"({self.op}, {self.arg1 or '_'}, {self.arg2 or '_'}, {self.result or '_'})"


class IRGenerator:
    """Walks AST and emits three-address code quadruples."""

    def __init__(self):
        self.quads = []
        self._t = 0
        self._l = 0

    def generate(self, program):
        for d in program.declarations:
            self._fn(d)
        return self.quads

    # ---- helpers ----

    def _temp(self):
        self._t += 1
        return f"t{self._t - 1}"

    def _label(self):
        self._l += 1
        return f"L{self._l - 1}"

    def _emit(self, op, a1=None, a2=None, r=None):
        self.quads.append(Quadruple(op, a1, a2, r))

    # ---- walkers ----

    def _fn(self, node):
        if not isinstance(node, FunctionDeclNode):
            return
        self._emit("func", node.name)
        for p in node.params:
            self._emit("param", p.name)
        if node.body:
            self._blk(node.body)
        self._emit("endfunc")

    def _blk(self, node):
        for s in node.statements:
            self._stmt(s)

    def _stmt(self, node):
        if isinstance(node, VarDeclStmtNode):
            if node.init_expr:
                val = self._expr(node.init_expr)
                self._emit("assign", val, None, node.name)
        elif isinstance(node, AssignStmtNode):
            val = self._expr(node.value)
            self._emit("assign", val, None, node.left.name)
        elif isinstance(node, ReturnStmtNode):
            if node.expr:
                self._emit("return", self._expr(node.expr))
            else:
                self._emit("return")
        elif isinstance(node, ExprStmtNode):
            if isinstance(node.expr, AssignStmtNode):
                self._stmt(node.expr)
            else:
                self._expr(node.expr)
        elif isinstance(node, IfStmtNode):
            self._if(node)
        elif isinstance(node, WhileStmtNode):
            self._while(node)
        elif isinstance(node, BlockStmtNode):
            self._blk(node)
        # EmptyStmtNode — no-op

    def _if(self, node):
        cond = self._expr(node.condition)
        e_lab = self._label()
        end_lab = self._label()
        self._emit("if_false", cond, None, e_lab)
        self._blk(node.then_block)
        self._emit("goto", None, None, end_lab)
        self._emit("label", None, None, e_lab)
        if node.else_block:
            if isinstance(node.else_block, IfStmtNode):
                self._if(node.else_block)
            else:
                self._blk(node.else_block)
        self._emit("label", None, None, end_lab)

    def _while(self, node):
        start = self._label()
        end = self._label()
        self._emit("label", None, None, start)
        cond = self._expr(node.condition)
        self._emit("if_false", cond, None, end)
        self._blk(node.body)
        self._emit("goto", None, None, start)
        self._emit("label", None, None, end)

    def _expr(self, node):
        """Evaluate expression, return the name holding its value (temp or var)."""
        if isinstance(node, NumberLiteralNode):
            t = self._temp()
            self._emit("=", str(node.value), None, t)
            return t
        if isinstance(node, LValueNode):
            return node.name
        if isinstance(node, UnaryMinusNode):
            v = self._expr(node.expr)
            t = self._temp()
            self._emit("neg", v, None, t)
            return t
        if isinstance(node, BinaryExprNode):
            left = self._expr(node.left)
            right = self._expr(node.right)
            t = self._temp()
            self._emit(node.op, left, right, t)
            return t
        if isinstance(node, FuncCallNode):
            for a in node.args:
                self._emit("arg", self._expr(a))
            t = self._temp()
            self._emit("call", node.name, str(len(node.args)), t)
            return t
        return None
