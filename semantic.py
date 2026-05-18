"""Minimal semantic analyzer: symbol table + basic checks"""

<<<<<<< HEAD
from compiler_ast import *
=======
from ast import *
>>>>>>> 661b9812f96a549b4a6fa1c00d5cf185523dd921


class SemanticAnalyzer:
    """Walks AST, builds scoped symbol table, checks errors."""

    def __init__(self):
        self.scopes = [{}]
        self.errors = []
        self._fn_return_type = None
        self._loop_depth = 0

    # ---- symbol table helpers ----

    def _enter(self):
        self.scopes.append({})

    def _exit(self):
        self.scopes.pop()

    def _define(self, name, kind, type_name="i32", mutable=False, init=False):
        self.scopes[-1][name] = dict(
            kind=kind, type=type_name, mutable=mutable, init=init
        )

    def _lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def _err(self, msg, node=None):
        line = getattr(node, "line", getattr(node, "name", ""))
        self.errors.append(f"  [{line}] {msg}")

    # ---- entry point ----

    def analyze(self, program):
        if not isinstance(program, ProgramNode):
            return self.errors
        self._enter()
        for d in program.declarations:
            self._visit_fn(d)
        self._exit()
        return self.errors

    # ---- visitors ----

    def _visit_fn(self, node):
        if not isinstance(node, FunctionDeclNode):
            return
        self._define(node.name, "function")
        self._enter()
        self._fn_return_type = node.return_type
        for p in node.params:
            self._define(
                p.name, "param",
                p.param_type.type_name if p.param_type else "i32",
                p.is_mutable, True
            )
        if node.body:
            self._visit_block(node.body)
        self._exit()
        self._fn_return_type = None

    def _visit_block(self, node):
        if not isinstance(node, BlockStmtNode):
            return
        self._enter()
        for s in node.statements:
            self._visit_stmt(s)
        self._exit()

    def _visit_stmt(self, node):
        if isinstance(node, VarDeclStmtNode):
            sym_type = node.var_type.type_name if node.var_type else "i32"
            self._define(node.name, "variable", sym_type, node.is_mutable,
                         init=node.init_expr is not None)
            if node.init_expr:
                self._visit_expr(node.init_expr)
        elif isinstance(node, AssignStmtNode):
            sym = self._lookup(node.left.name)
            if sym is None:
                self._err(f"变量 '{node.left.name}' 未声明", node.left)
            elif not sym["mutable"]:
                self._err(f"不可变变量 '{node.left.name}' 不能赋值", node.left)
            self._visit_expr(node.value)
        elif isinstance(node, ReturnStmtNode):
            if node.expr:
                self._visit_expr(node.expr)
        elif isinstance(node, IfStmtNode):
            self._visit_expr(node.condition)
            self._visit_block(node.then_block)
            if node.else_block:
                self._visit_stmt(node.else_block)
        elif isinstance(node, WhileStmtNode):
            self._loop_depth += 1
            self._visit_expr(node.condition)
            self._visit_block(node.body)
            self._loop_depth -= 1
        elif isinstance(node, ForStmtNode):
            self._loop_depth += 1
            # 循环变量定义在循环体作用域中
            self._enter()
            self._define(node.var_name, "variable", "i32", node.is_mutable, init=True)
            # 检查可迭代结构
            if isinstance(node.iterable, RangeNode):
                self._visit_expr(node.iterable.start)
                self._visit_expr(node.iterable.end)
            else:
                self._visit_expr(node.iterable)
            # 访问循环体
            self._visit_block(node.body)
            self._exit()
            self._loop_depth -= 1
        elif isinstance(node, ExprStmtNode):
            if isinstance(node.expr, AssignStmtNode):
                self._visit_stmt(node.expr)  # assignment inside ExprStmtNode
            else:
                self._visit_expr(node.expr)
        elif isinstance(node, BlockStmtNode):
            self._visit_block(node)
        # EmptyStmtNode — no-op

    def _visit_expr(self, node):
        if isinstance(node, BinaryExprNode):
            self._visit_expr(node.left)
            self._visit_expr(node.right)
        elif isinstance(node, UnaryMinusNode):
            self._visit_expr(node.expr)
        elif isinstance(node, LValueNode):
            sym = self._lookup(node.name)
            if sym is None:
                self._err(f"变量 '{node.name}' 未声明", node)
        elif isinstance(node, FuncCallNode):
            sym = self._lookup(node.name)
            if sym is None:
                self._err(f"函数 '{node.name}' 未声明", node)
            for a in node.args:
                self._visit_expr(a)
        elif isinstance(node, ArrayLiteralNode):
            for elem in node.elements:
                self._visit_expr(elem)
        elif isinstance(node, ArrayAccessNode):
            self._visit_expr(node.array)
            self._visit_expr(node.index)
        # NumberLiteralNode — no-op
