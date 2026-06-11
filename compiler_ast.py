"""Rust 类语言的 AST 节点定义"""

from typing import Any


class ASTNode:
    """所有 AST 节点的基类,统一携带源位置信息(line/column)。"""
    node_name = "ASTNode"

    def __init__(self, line: int = 0, column: int = 0):
        self.line = int(line)
        self.column = int(column)

    def __repr__(self):
        return f"<{self.node_name}@{self.line}:{self.column}>"

    def to_dict(self) -> dict:
        """将节点转换为字典格式，用于可视化"""
        result: dict = {"name": self.node_name, "line": self.line, "column": self.column}
        for attr, value in self.__dict__.items():
            if attr in ('line', 'column', 'node_name') or attr.startswith('_'):
                continue
            if isinstance(value, ASTNode):
                result[attr] = value.to_dict()
            elif isinstance(value, list):
                result[attr] = [v.to_dict() if isinstance(v, ASTNode) else v for v in value]
            else:
                result[attr] = value
        return result


class ProgramNode(ASTNode):
    """程序根节点 - 表示整个程序"""
    node_name = "Program"

    def __init__(self, declarations: list, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.declarations = declarations  # 函数声明列表 FunctionDeclNode


class FunctionDeclNode(ASTNode):
    """函数声明节点"""
    node_name = "FunctionDecl"

    def __init__(self, name: str, params: list, return_type, body,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name  # 函数名
        self.params = params  # 参数列表 ParamNode
        self.return_type = return_type  # 返回类型 TypeNode 或 None
        self.body = body  # 函数体 BlockStmtNode


class ParamNode(ASTNode):
    """函数参数节点"""
    node_name = "Param"

    def __init__(self, name: str, is_mutable: bool, param_type,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name  # 参数名
        self.is_mutable = is_mutable  # 是否可变
        self.param_type = param_type  # 参数类型 TypeNode


class TypeNode(ASTNode):
    """类型节点（如 i32）"""
    node_name = "Type"

    def __init__(self, type_name: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.type_name = type_name  # 类型名称，如 "i32"


class ArrayTypeNode(ASTNode):
    """数组类型节点: [Type; size]"""
    node_name = "ArrayType"

    def __init__(self, element_type, size: int,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.element_type = element_type  # 元素类型 TypeNode
        self.size = size  # 数组长度

    @property
    def type_name(self):
        return f"[{self.element_type.type_name}; {self.size}]"


class BlockStmtNode(ASTNode):
    """语句块节点"""
    node_name = "Block"

    def __init__(self, statements: list, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.statements = statements  # 语句列表


class EmptyStmtNode(ASTNode):
    """空语句节点（仅分号）"""
    node_name = "EmptyStmt"


class ReturnStmtNode(ASTNode):
    """返回语句节点"""
    node_name = "ReturnStmt"

    def __init__(self, expr=None, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expr = expr  # 返回表达式 ExprNode 或 None


class BreakStmtNode(ASTNode):
    """break 语句节点"""
    node_name = "BreakStmt"

    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(line, column)


class ContinueStmtNode(ASTNode):
    """continue 语句节点"""
    node_name = "ContinueStmt"

    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(line, column)


class VarDeclStmtNode(ASTNode):
    """变量声明语句节点"""
    node_name = "VarDeclStmt"

    def __init__(self, name: str, is_mutable: bool, var_type=None, init_expr=None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name  # 变量名
        self.is_mutable = is_mutable  # 是否可变
        self.var_type = var_type  # 类型注解 TypeNode 或 None
        self.init_expr = init_expr  # 初始化表达式 ExprNode 或 None


class AssignStmtNode(ASTNode):
    """赋值语句节点"""
    node_name = "AssignStmt"

    def __init__(self, left, value, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.left = left  # 左值 LValueNode
        self.value = value  # 右值表达式 ExprNode


class ExprStmtNode(ASTNode):
    """表达式语句节点"""
    node_name = "ExprStmt"

    def __init__(self, expr, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expr = expr  # 表达式 ExprNode


class IfStmtNode(ASTNode):
    """条件语句节点"""
    node_name = "IfStmt"

    def __init__(self, condition, then_block, else_block=None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.condition = condition  # 条件表达式 ExprNode
        self.then_block = then_block  # then 语句块 BlockStmtNode
        self.else_block = else_block  # else 语句块 BlockStmtNode 或 IfStmtNode 或 None


class WhileStmtNode(ASTNode):
    """while 循环语句节点"""
    node_name = "WhileStmt"

    def __init__(self, condition, body, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.condition = condition  # 循环条件 ExprNode
        self.body = body  # 循环体 BlockStmtNode


class ForStmtNode(ASTNode):
    """for 循环语句节点"""
    node_name = "ForStmt"

    def __init__(self, var_name: str, is_mutable: bool, iterable, body,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.var_name = var_name  # 循环变量名
        self.is_mutable = is_mutable  # 是否可变
        self.iterable = iterable  # 可迭代结构 (RangeNode)
        self.body = body  # 循环体 BlockStmtNode


class RangeNode(ASTNode):
    """范围表达式节点: start .. end"""
    node_name = "Range"

    def __init__(self, start, end, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.start = start  # 起始表达式
        self.end = end  # 结束表达式


class BinaryExprNode(ASTNode):
    """二元表达式节点"""
    node_name = "BinaryExpr"

    def __init__(self, op: str, left, right, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.op = op  # 运算符
        self.left = left  # 左操作数 ExprNode
        self.right = right  # 右操作数 ExprNode


class LValueNode(ASTNode):
    """左值节点 - 变量引用"""
    node_name = "LValue"

    def __init__(self, name: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name  # 变量名


class NumberLiteralNode(ASTNode):
    """数字字面量节点"""
    node_name = "NumberLiteral"

    def __init__(self, value, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = int(value)  # 数值


class FuncCallNode(ASTNode):
    """函数调用节点"""
    node_name = "FuncCall"

    def __init__(self, name: str, args: list, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name  # 函数名
        self.args = args  # 实参列表 ExprNode


class UnaryMinusNode(ASTNode):
    """一元负号表达式节点"""
    node_name = "UnaryMinus"

    def __init__(self, expr, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expr = expr  # 操作数 ExprNode


class ArrayLiteralNode(ASTNode):
    """数组字面量节点: [expr, expr, ...]"""
    node_name = "ArrayLiteral"

    def __init__(self, elements: list, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.elements = elements  # 元素表达式列表


class ArrayAccessNode(ASTNode):
    """数组下标访问节点: arr[index]"""
    node_name = "ArrayAccess"

    def __init__(self, array, index, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.array = array  # 数组表达式
        self.index = index  # 下标表达式
