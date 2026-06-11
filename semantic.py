"""语义分析器:符号表 + 类型检查 + 静态错误诊断。

实现类 Rust 语言的静态语义检查:作用域感知的符号表(支持 let 重影)、
类型检查、左值与可变性规则、函数调用与返回类型一致性、控制流约束等。
诊断信息携带行/列号和稳定错误码,供前端渲染。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from compiler_ast import *


# --------------------------------------------------------------------------- #
# 错误报告                                                                      #
# --------------------------------------------------------------------------- #

# 错误码,前端按此过滤/着色。
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
    """单条静态语义错误。"""
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
# 符号表                                                                        #
# --------------------------------------------------------------------------- #

# AST 节点暂未携带源位置;此处保留钩子供未来解析器接入,缺失时回退 (0, 0)。
def _pos(node: Any) -> tuple[int, int]:
    line = getattr(node, "line", 0) or 0
    col = getattr(node, "column", 0) or 0
    return int(line), int(col)


@dataclass
class Symbol:
    name: str
    kind: str            # 'fn' | 'var' | 'param'
    type_name: str       # 函数为 'i32' 或 'void'
    mutable: bool = False
    initialized: bool = False
    # 声明处的源位置(用于未初始化等错误定位)
    decl_line: int = 0
    decl_column: int = 0
    # 仅对函数有意义
    params: List["ParamSymbol"] = field(default_factory=list)
    has_return: bool = False


@dataclass
class ParamSymbol:
    name: str
    type_name: str
    mutable: bool


# 语言内置符号
BUILTIN_SYMBOLS: Dict[str, Symbol] = {}


class SymbolTable:
    """作用域栈:每个作用域是一个将名字映射到 Symbol 的字典。

    除栈式作用域外,还维护一个扁平注册表 `all`,作用域弹出后仍能查询
    历史上出现过的所有符号,供前端符号表面板使用。
    """

    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]
        self.all: Dict[str, Symbol] = {}

    # -- 作用域管理 --
    def enter(self) -> None:
        self.scopes.append({})

    def exit(self) -> None:
        if len(self.scopes) > 1:
            self.scopes.pop()

    # -- 操作 --
    def define(self, sym: Symbol) -> None:
        """定义 `sym`;同作用域内同名绑定被覆盖(let 重影)。"""
        self.scopes[-1][sym.name] = sym
        self.all[sym.name] = sym

    def lookup(self, name: str) -> Optional[Symbol]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_local(self, name: str) -> Optional[Symbol]:
        return self.scopes[-1].get(name)

    def all_symbols(self) -> Dict[str, Symbol]:
        return self.all


# --------------------------------------------------------------------------- #
# Type helpers                                                                 #
# --------------------------------------------------------------------------- #

TYPE_I32 = "i32"
TYPE_VOID = "void"
TYPE_BOOL = "i32"   # 布尔值复用 i32(0 / 1)

# 要求整型操作数、返回 i32 的运算符
INT_BINOPS = {"+", "-", "*", "/"}
CMP_BINOPS  = {"<", "<=", ">", ">=", "==", "!="}


def type_of_type_node(node: Any) -> str:
    """返回 TypeNode / ArrayTypeNode 的规范类型名。"""
    if node is None:
        return TYPE_VOID
    if isinstance(node, ArrayTypeNode):
        return f"[{type_of_type_node(node.element_type)};{node.size}]"
    if isinstance(node, TypeNode):
        return node.type_name
    return TYPE_VOID


# --------------------------------------------------------------------------- #
# 语义分析器                                                                    #
# --------------------------------------------------------------------------- #

class SemanticAnalyzer:
    """遍历 AST、构建符号表、执行类型检查,并收集 :class:`SemanticError` 列表。"""

    def __init__(self, require_main: bool = False):
        self.symbols = SymbolTable()
        self.errors: List[SemanticError] = []
        self._current_fn: Optional[Symbol] = None
        self._loop_depth: int = 0
        self._has_main: bool = False
        self._require_main: bool = require_main
        # 绑定内置符号
        for name, sym in BUILTIN_SYMBOLS.items():
            self.symbols.define(sym)

    # ---- 诊断 ----

    def _err(self, code: str, message: str, node: Any) -> None:
        line, col = _pos(node)
        self.errors.append(SemanticError(
            code=code, message=message,
            line=line, column=col,
            node_name=getattr(node, "node_name", type(node).__name__),
        ))

    # ---- 入口 ----

    def analyze(self, program: ProgramNode) -> List[SemanticError]:
        self.errors = []
        self._has_main = False

        if not isinstance(program, ProgramNode):
            return self.errors

        # 第一遍:收集函数签名,允许任意顺序定义与前向引用。
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

        # 第二遍:详细访问每个函数体。
        for decl in program.declarations:
            if isinstance(decl, FunctionDeclNode):
                if decl.name == "main":
                    self._has_main = True
                self._visit_fn(decl)

        if self._require_main and not self._has_main:
            self._err(E_MAIN_MISSING, "缺少 main 函数", program)

        return self.errors

    # ---- 声明 ----

    def _visit_fn(self, node: FunctionDeclNode) -> None:
        fn_sym = self.symbols.lookup(node.name)
        if fn_sym is None:
            # 第一遍已上报为重复定义,这里补建一个临时符号,继续访问函数体。
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
        # 形参
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
        declared = type_of_type_node(node.return_type)
        if declared != TYPE_VOID and not fn_sym.has_return:
            self._err(
                E_MISSING_RETURN,
                f"函数 '{node.name}' 声明返回 {declared}，但缺少 return 语句",
                node,
            )
        self.symbols.exit()
        self._current_fn = None

    # ---- 语句 ----

    def _visit_block(self, node: BlockStmtNode) -> None:
        self.symbols.enter()
        for s in node.statements:
            self._visit_stmt(s)
        # 块退出前,扫描本作用域内未初始化的变量
        self._check_uninitialized_in_current_scope()
        self.symbols.exit()

    def _check_uninitialized_in_current_scope(self) -> None:
        """对当前作用域内仍未初始化的 var 报 E_UNINITIALIZED。

        位置取自声明时的 decl_line/decl_column(由 VarDeclStmtNode 提供)。
        """
        for sym in self.symbols.scopes[-1].values():
            if sym.kind == "var" and not sym.initialized:
                err = SemanticError(
                    code=E_UNINITIALIZED,
                    message=f"变量 '{sym.name}' 声明后未初始化",
                    line=sym.decl_line,
                    column=sym.decl_column,
                    node_name="VarDeclStmt",
                )
                self.errors.append(err)

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

        if isinstance(node, BreakStmtNode):
            if self._loop_depth <= 0:
                self._err(E_BREAK_OUTSIDE,
                          "break 语句出现在循环体外", node)
            return

        if isinstance(node, ContinueStmtNode):
            if self._loop_depth <= 0:
                self._err(E_CONTINUE_OUTSIDE,
                          "continue 语句出现在循环体外", node)
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

        if isinstance(node, LoopStmtNode):
            # loop 无条件——一直运行直到遇到 break
            self._loop_depth += 1
            self._visit_block(node.body)
            self._loop_depth -= 1
            return

        if isinstance(node, ForStmtNode):
            # 循环变量定义在循环体作用域内
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
            # 解析器把"作为语句的赋值"包在 ExprStmtNode 中,这里解包后转交 _visit_assign
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
                # 类型推断:取右值类型,缺省 i32
                decl_type = rhs_t or TYPE_I32
            else:
                if rhs_t is not None and rhs_t != decl_type:
                    self._err(E_TYPE_MISMATCH,
                              f"变量 '{node.name}' 声明类型 {decl_type} 与初始值类型 {rhs_t} 不匹配",
                              node)
        # 无初始化表达式:留待首次赋值推断,缺省按 i32 处理。
        if decl_type is None:
            decl_type = TYPE_I32

        # 允许同作用域重复声明(重影);新绑定覆盖旧绑定。
        self.symbols.define(Symbol(
            name=node.name, kind="var",
            type_name=decl_type, mutable=node.is_mutable,
            initialized=node.init_expr is not None,
            decl_line=node.line, decl_column=node.column,
        ))

    def _visit_assign(self, node: AssignStmtNode) -> None:
        left = node.left
        if isinstance(left, LValueNode):
            sym = self.symbols.lookup(left.name)
            if sym is None:
                self._err(E_UNDEFINED_VAR,
                          f"变量 '{left.name}' 未声明", left)
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
        elif isinstance(left, ArrayAccessNode):
            # 数组元素赋值：a[i] = expr
            if isinstance(left.array, LValueNode):
                sym = self.symbols.lookup(left.array.name)
                if sym is None:
                    self._err(E_UNDEFINED_VAR,
                              f"数组 '{left.array.name}' 未声明", left.array)
                    self._visit_expr(node.value)
                    return
                if not sym.mutable:
                    self._err(E_NOT_MUTABLE,
                              f"不可变数组 '{left.array.name}' 的元素不能被赋值", left.array)
            # 下标必须为 i32
            idx_t = self._visit_expr(left.index)
            if idx_t is not None and idx_t != TYPE_I32:
                self._err(E_TYPE_MISMATCH,
                          f"数组下标必须为 i32，实际为 {idx_t}", left.index)
            # 右值类型须与数组元素类型匹配
            arr_t = self._visit_expr(left.array) or ""
            rhs_t = self._visit_expr(node.value)
            if arr_t.startswith("[") and ";" in arr_t:
                elem_t = arr_t[1:arr_t.index(";")]
                if rhs_t is not None and rhs_t != elem_t:
                    self._err(E_TYPE_MISMATCH,
                              f"数组元素赋值类型不匹配：元素类型为 {elem_t}，右值为 {rhs_t}",
                              node)
        else:
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

    # ---- 表达式 ----

    def _visit_expr(self, node: Any) -> Optional[str]:
        """访问表达式并返回其推断类型;类型错误返回 ``None``(错误已上报)。"""
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
                # 函数名仅在调用表达式中合法,直接当值用视作不合法左值
                self._err(E_NOT_LVALUE,
                          f"函数名 '{node.name}' 只能通过调用表达式使用", node)
                return TYPE_VOID
            if not sym.initialized:
                self._err(E_UNINITIALIZED,
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
            # 未知运算符:解析器已处理,此处软失败。
            return TYPE_I32

        if isinstance(node, FuncCallNode):
            sym = self.symbols.lookup(node.name)
            if sym is None or sym.kind != "fn":
                self._err(E_UNDEFINED_FN,
                          f"函数 '{node.name}' 未声明", node)
                for a in node.args:           # 仍访问实参,暴露嵌套错误
                    self._visit_expr(a)
                return None
            if len(node.args) != len(sym.params):
                self._err(E_ARITY,
                          f"函数 '{node.name}' 需要 {len(sym.params)} 个参数，"
                          f"实际传入 {len(node.args)} 个",
                          node)
            for i, arg in enumerate(node.args):
                at = self._visit_expr(arg)
                if i < len(sym.params) and at is not None:
                    expect = sym.params[i].type_name
                    if at != expect:
                        self._err(E_ARG_TYPE,
                                  f"函数 '{node.name}' 第 {i + 1} 个参数应为 {expect}，"
                                  f"实际为 {at}",
                                  arg)
            if sym.type_name == TYPE_VOID:    # void 函数不能作为值使用
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
            # 数组类型去掉一维得到元素类型,如 "[i32;3]" -> "i32"
            if arr_t.startswith("[") and ";" in arr_t:
                return arr_t[1:arr_t.index(";")]
            return TYPE_I32

        if isinstance(node, RangeNode):
            # 仅出现在 for-in 中,本身不作为值使用
            s = self._visit_expr(node.start) or TYPE_I32
            e = self._visit_expr(node.end) or TYPE_I32
            if s != TYPE_I32 or e != TYPE_I32:
                self._err(E_TYPE_MISMATCH,
                          f"for 范围表达式必须为 i32，实际为 {s}..{e}", node)
            return None

        return None


# --------------------------------------------------------------------------- #
# 入口                                                                          #
# --------------------------------------------------------------------------- #

def analyze(program: ProgramNode) -> List[SemanticError]:
    """前端调用的函数式入口。"""
    return SemanticAnalyzer().analyze(program)
