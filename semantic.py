"""Semantic analyzer: symbol table + type checking + static error diagnostics.

Implements the static semantic checks required by the CompilerLab assignment
(§0.1 ~ §5.1):

  * Scope-aware symbol table with "重影" (shadowing) on let.
  * Type checking for i32 — currently the only supported type.
  * L-value rules: assignment target must be a declared mutable variable
    and the RHS type must match.
  * Function calls: arity, argument types, return-value usage.
  * Function return type must match the expression type in `return`.
  * `if` / `while` condition must be i32.
  * Diagnostics carry line / column info and a stable error code so the
    front-end can render them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from compiler_ast import *


# --------------------------------------------------------------------------- #
# Error reporting                                                              #
# --------------------------------------------------------------------------- #

# Error codes — stable identifiers used by the front-end.
E_UNDEFINED_VAR      = "E_UNDEFINED_VAR"
E_UNDEFINED_FN       = "E_UNDEFINED_FN"
E_REDECLARE_PARAM    = "E_REDECLARE_PARAM"
E_REDECLARE_VAR      = "E_REDECLARE_VAR"
E_DUPLICATE_FN       = "E_DUPLICATE_FN"
E_NOT_MUTABLE        = "E_NOT_MUTABLE"
E_TYPE_MISMATCH      = "E_TYPE_MISMATCH"
E_RETURN_TYPE        = "E_RETURN_TYPE"
E_MISSING_RETURN     = "E_MISSING_RETURN"
E_ARITY              = "E_ARITY"
E_ARG_TYPE           = "E_ARG_TYPE"
E_VOID_USED          = "E_VOID_USED"
E_NOT_LVALUE         = "E_NOT_LVALUE"
E_COND_NOT_BOOL      = "E_COND_NOT_BOOL"
E_BREAK_OUTSIDE      = "E_BREAK_OUTSIDE"
E_CONTINUE_OUTSIDE   = "E_CONTINUE_OUTSIDE"
E_MAIN_MISSING       = "E_MAIN_MISSING"
E_UNINITIALIZED      = "E_UNINITIALIZED"


@dataclass
class SemanticError:
    """A single static semantic error."""
    code: str
    message: str
    line: int = 0
    column: int = 0
    node_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "node": self.node_name,
        }


# --------------------------------------------------------------------------- #
# Symbol table                                                                 #
# --------------------------------------------------------------------------- #

# We don't have source positions on AST nodes (lexer tokens do, but the AST
# builder doesn't propagate them). For now we expose a hook so a future
# parser that records line numbers can plug in; for diagnostics we fall back
# to 0/0.
def _pos(node: Any) -> tuple[int, int]:
    line = getattr(node, "line", 0) or 0
    col = getattr(node, "column", 0) or 0
    return int(line), int(col)


@dataclass
class Symbol:
    name: str
    kind: str            # 'fn' | 'var' | 'param'
    type_name: str       # 'i32' or 'void' for functions
    mutable: bool = False
    initialized: bool = False
    # For functions
    params: List["ParamSymbol"] = field(default_factory=list)
    has_return: bool = False   # whether the function actually returns a value


@dataclass
class ParamSymbol:
    name: str
    type_name: str
    mutable: bool


# Built-in symbols that the language provides.
BUILTIN_SYMBOLS: Dict[str, Symbol] = {}


class SymbolTable:
    """Stack of scopes. Each scope is a dict mapping name -> Symbol."""

    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]
        # A flat registry of every symbol ever defined. The UI uses this
        # to display the symbol table after analysis finishes (when
        # scopes have already been popped). Lookups still walk the
        # scope stack, but definitions are recorded here too.
        self.all: Dict[str, Symbol] = {}

    # -- scope management --
    def enter(self) -> None:
        self.scopes.append({})

    def exit(self) -> None:
        if len(self.scopes) > 1:
            self.scopes.pop()

    # -- operations --
    def define(self, sym: Symbol) -> None:
        """Define `sym` in the current scope, overwriting any same-scope
        binding (lets re-declarations shadow within the same block).
        """
        self.scopes[-1][sym.name] = sym
        # Also keep a flat copy. Latest definition wins; for the front-end
        # this is fine because shadowed vars share a name anyway.
        self.all[sym.name] = sym

    def lookup(self, name: str) -> Optional[Symbol]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_local(self, name: str) -> Optional[Symbol]:
        return self.scopes[-1].get(name)

    def all_symbols(self) -> Dict[str, Symbol]:
        """Return the flat registry of every symbol seen so far."""
        return self.all


# --------------------------------------------------------------------------- #
# Type helpers                                                                 #
# --------------------------------------------------------------------------- #

TYPE_I32 = "i32"
TYPE_VOID = "void"
TYPE_BOOL = "i32"   # booleans are encoded as i32 (0 / 1)

# Operators that require integer operands and return i32.
INT_BINOPS = {"+", "-", "*", "/"}
# Comparison operators return i32 (0 / 1).
CMP_BINOPS = {"<", "<=", ">", ">=", "==", "!="}


def type_of_type_node(node: Any) -> str:
    """Return the canonical type name for a TypeNode / ArrayTypeNode."""
    if node is None:
        return TYPE_VOID
    if isinstance(node, ArrayTypeNode):
        return f"[{type_of_type_node(node.element_type)};{node.size}]"
    if isinstance(node, TypeNode):
        return node.type_name
    return TYPE_VOID


# --------------------------------------------------------------------------- #
# Semantic Analyzer                                                            #
# --------------------------------------------------------------------------- #

class SemanticAnalyzer:
    """Walks the AST, builds a scoped symbol table, performs type checks,
    and collects a list of :class:`SemanticError`.
    """

    def __init__(self, require_main: bool = False):
        self.symbols = SymbolTable()
        self.errors: List[SemanticError] = []
        self._current_fn: Optional[Symbol] = None
        self._loop_depth: int = 0
        self._has_main: bool = False
        self._require_main: bool = require_main
        # Bind built-ins
        for name, sym in BUILTIN_SYMBOLS.items():
            self.symbols.define(sym)

    # ---- diagnostics ----

    def _err(self, code: str, message: str, node: Any) -> None:
        line, col = _pos(node)
        self.errors.append(SemanticError(
            code=code, message=message,
            line=line, column=col,
            node_name=getattr(node, "node_name", type(node).__name__),
        ))

    # ---- entry point ----

    def analyze(self, program: ProgramNode) -> List[SemanticError]:
        self.errors = []
        self._has_main = False

        if not isinstance(program, ProgramNode):
            return self.errors

        # ---- Pass 1: collect all top-level function signatures so calls
        #      to forward-referenced functions don't get flagged as undefined.
        #      Rust actually doesn't allow forward calls without decl, but
        #      the assignment doesn't pin that down — we accept any order.
        for decl in program.declarations:
            if isinstance(decl, FunctionDeclNode):
                if self.symbols.lookup_local(decl.name) is not None:
                    self._err(E_DUPLICATE_FN,
                              f"函数 '{decl.name}' 重复定义", decl)
                else:
                    self.symbols.define(Symbol(
                        name=decl.name,
                        kind="fn",
                        type_name=type_of_type_node(decl.return_type),
                        params=[
                            ParamSymbol(p.name, type_of_type_node(p.param_type), p.is_mutable)
                            for p in decl.params
                        ],
                    ))

        # ---- Pass 2: visit every function body in detail.
        for decl in program.declarations:
            if isinstance(decl, FunctionDeclNode):
                if decl.name == "main":
                    self._has_main = True
                self._visit_fn(decl)

        if self._require_main and not self._has_main:
            self._err(E_MAIN_MISSING, "缺少 main 函数", program)

        return self.errors

    # ---- declarations ----

    def _visit_fn(self, node: FunctionDeclNode) -> None:
        fn_sym = self.symbols.lookup(node.name)
        if fn_sym is None:
            # Already reported as duplicate during pass 1; still visit body
            # to surface nested errors rather than silently dropping them.
            fn_sym = Symbol(
                name=node.name, kind="fn",
                type_name=type_of_type_node(node.return_type),
                params=[
                    ParamSymbol(p.name, type_of_type_node(p.param_type), p.is_mutable)
                    for p in node.params
                ],
            )
        self._current_fn = fn_sym
        self.symbols.enter()
        # parameters
        for p in node.params:
            if self.symbols.lookup_local(p.name) is not None:
                self._err(E_REDECLARE_PARAM,
                          f"参数 '{p.name}' 重复声明", p)
            self.symbols.define(Symbol(
                name=p.name, kind="param",
                type_name=type_of_type_node(p.param_type),
                mutable=p.is_mutable,
                initialized=True,
            ))
        if node.body:
            self._visit_block(node.body)
        # Check return type vs actual returns
        declared = type_of_type_node(node.return_type)
        if declared != TYPE_VOID and not fn_sym.has_return:
            self._err(
                E_MISSING_RETURN,
                f"函数 '{node.name}' 声明返回 {declared}，但缺少 return 语句",
                node,
            )
        self.symbols.exit()
        self._current_fn = None

    # ---- statements ----

    def _visit_block(self, node: BlockStmtNode) -> None:
        self.symbols.enter()
        for s in node.statements:
            self._visit_stmt(s)
        self.symbols.exit()

    def _visit_stmt(self, node: Any) -> None:
        if isinstance(node, EmptyStmtNode):
            return

        if isinstance(node, BlockStmtNode):
            self._visit_block(node)
            return

        if isinstance(node, VarDeclStmtNode):
            self._visit_var_decl(node)
            return

        if isinstance(node, AssignStmtNode):
            self._visit_assign(node)
            return

        if isinstance(node, ReturnStmtNode):
            self._visit_return(node)
            return

        if isinstance(node, IfStmtNode):
            cond_t = self._visit_expr(node.condition)
            if cond_t is not None and cond_t not in (TYPE_I32, TYPE_BOOL):
                self._err(E_COND_NOT_BOOL,
                          f"if 条件类型必须为 i32，实际为 {cond_t}", node.condition)
            self._visit_block(node.then_block)
            if node.else_block is not None:
                if isinstance(node.else_block, IfStmtNode):
                    self._visit_stmt(node.else_block)
                else:
                    self._visit_block(node.else_block)
            return

        if isinstance(node, WhileStmtNode):
            cond_t = self._visit_expr(node.condition)
            if cond_t is not None and cond_t not in (TYPE_I32, TYPE_BOOL):
                self._err(E_COND_NOT_BOOL,
                          f"while 条件类型必须为 i32，实际为 {cond_t}", node.condition)
            self._loop_depth += 1
            self._visit_block(node.body)
            self._loop_depth -= 1
            return

        if isinstance(node, ForStmtNode):
            # Loop variable is defined in the loop body scope.
            if isinstance(node.iterable, RangeNode):
                start_t = self._visit_expr(node.iterable.start) or TYPE_I32
                end_t   = self._visit_expr(node.iterable.end)   or TYPE_I32
                for tt, side in [(start_t, "起点"), (end_t, "终点")]:
                    if tt not in (TYPE_I32,):
                        self._err(E_TYPE_MISMATCH,
                                  f"for 范围{side}必须为 i32，实际为 {tt}",
                                  node.iterable)
            else:
                iter_t = self._visit_expr(node.iterable) or TYPE_I32
                if iter_t != TYPE_I32:
                    self._err(E_TYPE_MISMATCH,
                              f"for 迭代表达式必须为 i32，实际为 {iter_t}",
                              node.iterable)
            self._loop_depth += 1
            self.symbols.enter()
            self.symbols.define(Symbol(
                name=node.var_name, kind="var",
                type_name=TYPE_I32, mutable=node.is_mutable,
                initialized=True,
            ))
            self._visit_block(node.body)
            self.symbols.exit()
            self._loop_depth -= 1
            return

        if isinstance(node, ExprStmtNode):
            # Parser wraps an assignment-as-statement in ExprStmtNode
            # (see try_parse_expression / parse_statement). Unwrap so
            # the assignment gets full type & mutability checks.
            inner = node.expr
            if isinstance(inner, AssignStmtNode):
                self._visit_assign(inner)
                return
            self._visit_expr(inner)
            return

    def _visit_var_decl(self, node: VarDeclStmtNode) -> None:
        decl_type = type_of_type_node(node.var_type) if node.var_type else None
        if node.init_expr is not None:
            rhs_t = self._visit_expr(node.init_expr)
            if decl_type is None:
                # type inference: take the RHS type (default i32)
                decl_type = rhs_t or TYPE_I32
            else:
                if rhs_t is not None and rhs_t != decl_type:
                    self._err(E_TYPE_MISMATCH,
                              f"变量 '{node.name}' 声明类型 {decl_type} 与初始值类型 {rhs_t} 不匹配",
                              node)
        # else: no initializer — type may be inferred later from the first
        # assignment. We mark the variable as uninitialized; the IR layer
        # defaults the slot type to i32 which matches the assignment path.

        # Re-declaration is *allowed* (shadowing / 重影) — the spec
        # explicitly says each let shadows the previous binding.
        if decl_type is None:
            decl_type = TYPE_I32   # best-effort default; type-mismatch
                                    # will surface on first use
        self.symbols.define(Symbol(
            name=node.name, kind="var",
            type_name=decl_type, mutable=node.is_mutable,
            initialized=node.init_expr is not None,
        ))

    def _visit_assign(self, node: AssignStmtNode) -> None:
        left = node.left
        if isinstance(left, LValueNode):
            sym = self.symbols.lookup(left.name)
            if sym is None:
                self._err(E_UNDEFINED_VAR,
                          f"变量 '{left.name}' 未声明", left)
                # Even if undefined, still visit RHS to surface more errors.
                self._visit_expr(node.value)
                return
            if sym.kind == "fn":
                self._err(E_NOT_LVALUE,
                          f"函数名 '{left.name}' 不能作为左值", left)
                self._visit_expr(node.value)
                return
            if not sym.mutable:
                self._err(E_NOT_MUTABLE,
                          f"不可变变量 '{left.name}' 不能被赋值（需用 mut 声明）", left)
            rhs_t = self._visit_expr(node.value)
            if rhs_t is not None and sym.type_name != rhs_t:
                self._err(E_TYPE_MISMATCH,
                          f"赋值类型不匹配：'{left.name}' 为 {sym.type_name}，右值为 {rhs_t}",
                          node)
            sym.initialized = True
        else:
            # Non-lvalue on the left is already a parser error, but be safe.
            self._err(E_NOT_LVALUE, "赋值左值不合法", left)
            self._visit_expr(node.value)

    def _visit_return(self, node: ReturnStmtNode) -> None:
        if self._current_fn is None:
            self._err(E_RETURN_TYPE, "return 出现在函数外", node)
            return
        declared = self._current_fn.type_name
        if node.expr is None:
            if declared != TYPE_VOID:
                self._err(E_RETURN_TYPE,
                          f"函数 '{self._current_fn.name}' 应返回 {declared}，但 return 没有表达式",
                          node)
            return
        rhs_t = self._visit_expr(node.expr)
        if rhs_t is not None and rhs_t != declared and declared != TYPE_VOID:
            self._err(E_RETURN_TYPE,
                      f"函数 '{self._current_fn.name}' 声明返回 {declared}，"
                      f"实际返回 {rhs_t}", node)
        self._current_fn.has_return = True

    # ---- expressions ----

    def _visit_expr(self, node: Any) -> Optional[str]:
        """Visit an expression and return its inferred type.
        Returns ``None`` for type errors (already reported).
        """
        if node is None:
            return None
        if isinstance(node, NumberLiteralNode):
            return TYPE_I32
        if isinstance(node, LValueNode):
            sym = self.symbols.lookup(node.name)
            if sym is None:
                self._err(E_UNDEFINED_VAR,
                          f"变量 '{node.name}' 未声明", node)
                return None
            if sym.kind == "fn":
                # Using a function name as a value — only legal as a call.
                self._err(E_NOT_LVALUE,
                          f"函数名 '{node.name}' 只能通过调用表达式使用", node)
                return TYPE_VOID
            if not sym.initialized:
                self._err(E_UNDEFINED_VAR,
                          f"变量 '{node.name}' 尚未初始化", node)
            return sym.type_name

        if isinstance(node, UnaryMinusNode):
            inner = self._visit_expr(node.expr)
            if inner is not None and inner != TYPE_I32:
                self._err(E_TYPE_MISMATCH,
                          f"一元负号运算的操作数必须为 i32，实际为 {inner}", node)
            return TYPE_I32

        if isinstance(node, BinaryExprNode):
            lt = self._visit_expr(node.left)
            rt = self._visit_expr(node.right)
            if lt is not None and rt is not None and lt != rt:
                self._err(E_TYPE_MISMATCH,
                          f"运算符 '{node.op}' 的左右操作数类型不一致：{lt} vs {rt}", node)
            if node.op in INT_BINOPS:
                if lt is not None and lt != TYPE_I32:
                    self._err(E_TYPE_MISMATCH,
                              f"算术运算 '{node.op}' 需要 i32 操作数，实际为 {lt}", node)
                if rt is not None and rt != TYPE_I32:
                    self._err(E_TYPE_MISMATCH,
                              f"算术运算 '{node.op}' 需要 i32 操作数，实际为 {rt}", node)
                return TYPE_I32
            if node.op in CMP_BINOPS:
                if lt is not None and lt != TYPE_I32:
                    self._err(E_TYPE_MISMATCH,
                              f"比较运算 '{node.op}' 需要 i32 操作数，实际为 {lt}", node)
                if rt is not None and rt != TYPE_I32:
                    self._err(E_TYPE_MISMATCH,
                              f"比较运算 '{node.op}' 需要 i32 操作数，实际为 {rt}", node)
                return TYPE_I32
            # Unknown operator (parser already caught it) — fail soft.
            return TYPE_I32

        if isinstance(node, FuncCallNode):
            sym = self.symbols.lookup(node.name)
            if sym is None or sym.kind != "fn":
                self._err(E_UNDEFINED_FN,
                          f"函数 '{node.name}' 未声明", node)
                # Still visit args to surface nested errors.
                for a in node.args:
                    self._visit_expr(a)
                return None
            # arity
            if len(node.args) != len(sym.params):
                self._err(E_ARITY,
                          f"函数 '{node.name}' 需要 {len(sym.params)} 个参数，"
                          f"实际传入 {len(node.args)} 个",
                          node)
            # arg types
            for i, arg in enumerate(node.args):
                at = self._visit_expr(arg)
                if i < len(sym.params) and at is not None:
                    expect = sym.params[i].type_name
                    if at != expect:
                        self._err(E_ARG_TYPE,
                                  f"函数 '{node.name}' 第 {i + 1} 个参数应为 {expect}，"
                                  f"实际为 {at}",
                                  arg)
            # If the function has no return value, it can't be used as a
            # value (assignment RHS, operand, return value).
            if sym.type_name == TYPE_VOID:
                self._err(E_VOID_USED,
                          f"函数 '{node.name}' 没有返回值，不能作为右值参与运算",
                          node)
                return None
            return sym.type_name

        if isinstance(node, ArrayLiteralNode):
            if not node.elements:
                return None
            first = self._visit_expr(node.elements[0])
            for elem in node.elements[1:]:
                et = self._visit_expr(elem)
                if first is not None and et is not None and et != first:
                    self._err(E_TYPE_MISMATCH,
                              f"数组字面量元素类型不一致：{first} vs {et}", elem)
            return f"[{first or TYPE_I32};{len(node.elements)}]"

        if isinstance(node, ArrayAccessNode):
            arr_t = self._visit_expr(node.array) or ""
            idx_t = self._visit_expr(node.index)
            if idx_t is not None and idx_t != TYPE_I32:
                self._err(E_TYPE_MISMATCH,
                          f"数组下标必须为 i32，实际为 {idx_t}", node.index)
            # Strip one dimension off the array type for the element type.
            if arr_t.startswith("[") and ";" in arr_t:
                # e.g. "[i32;3]" -> "i32"
                inner = arr_t[1:arr_t.index(";")]
                return inner
            return TYPE_I32

        if isinstance(node, RangeNode):
            # Used only in for-in iterables; not a real value.
            s = self._visit_expr(node.start) or TYPE_I32
            e = self._visit_expr(node.end) or TYPE_I32
            if s != TYPE_I32 or e != TYPE_I32:
                self._err(E_TYPE_MISMATCH,
                          f"for 范围表达式必须为 i32，实际为 {s}..{e}", node)
            return None

        return None


# --------------------------------------------------------------------------- #
# Convenience wrapper                                                          #
# --------------------------------------------------------------------------- #

def analyze(program: ProgramNode) -> List[SemanticError]:
    """Functional entry point used by the front-end."""
    return SemanticAnalyzer().analyze(program)
