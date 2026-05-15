"""AST nodes for Rust-like language"""


class ASTNode:
    """Base class for all AST nodes"""
    node_name = "ASTNode"

    def __repr__(self):
        return f"<{self.node_name}>"

    def to_dict(self):
        """Convert node to dictionary for visualization"""
        result = {"name": self.node_name}
        for attr, value in self.__dict__.items():
            if attr != 'node_name' and not attr.startswith('_'):
                if isinstance(value, ASTNode):
                    result[attr] = value.to_dict()
                elif isinstance(value, list):
                    result[attr] = [v.to_dict() if isinstance(v, ASTNode) else v for v in value]
                else:
                    result[attr] = value
        return result


class ProgramNode(ASTNode):
    """Root node for the entire program"""
    node_name = "Program"

    def __init__(self, declarations):
        self.declarations = declarations  # list of FunctionDeclNode


class FunctionDeclNode(ASTNode):
    """Function declaration node"""
    node_name = "FunctionDecl"

    def __init__(self, name, params, return_type, body):
        self.name = name
        self.params = params  # list of ParamNode
        self.return_type = return_type  # TypeNode or None
        self.body = body  # BlockStmtNode


class ParamNode(ASTNode):
    """Function parameter node"""
    node_name = "Param"

    def __init__(self, name, is_mutable, param_type):
        self.name = name
        self.is_mutable = is_mutable  # bool
        self.param_type = param_type  # TypeNode


class TypeNode(ASTNode):
    """Type node (e.g., i32)"""
    node_name = "Type"

    def __init__(self, type_name):
        self.type_name = type_name  # string like "i32"


class BlockStmtNode(ASTNode):
    """Block statement node"""
    node_name = "Block"

    def __init__(self, statements):
        self.statements = statements  # list of statement nodes


class EmptyStmtNode(ASTNode):
    """Empty statement node (just semicolon)"""
    node_name = "EmptyStmt"


class ReturnStmtNode(ASTNode):
    """Return statement node"""
    node_name = "ReturnStmt"

    def __init__(self, expr=None):
        self.expr = expr  # ExprNode or None


class VarDeclStmtNode(ASTNode):
    """Variable declaration statement node"""
    node_name = "VarDeclStmt"

    def __init__(self, name, is_mutable, var_type=None, init_expr=None):
        self.name = name
        self.is_mutable = is_mutable  # bool
        self.var_type = var_type  # TypeNode or None
        self.init_expr = init_expr  # ExprNode or None


class AssignStmtNode(ASTNode):
    """Assignment statement node"""
    node_name = "AssignStmt"

    def __init__(self, left, value):
        self.left = left  # LValueNode
        self.value = value  # ExprNode


class ExprStmtNode(ASTNode):
    """Expression statement node"""
    node_name = "ExprStmt"

    def __init__(self, expr):
        self.expr = expr  # ExprNode


class IfStmtNode(ASTNode):
    """If statement node"""
    node_name = "IfStmt"

    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition  # ExprNode
        self.then_block = then_block  # BlockStmtNode
        self.else_block = else_block  # BlockStmtNode or IfStmtNode or None


class WhileStmtNode(ASTNode):
    """While loop statement node"""
    node_name = "WhileStmt"

    def __init__(self, condition, body):
        self.condition = condition  # ExprNode
        self.body = body  # BlockStmtNode


class BinaryExprNode(ASTNode):
    """Binary expression node"""
    node_name = "BinaryExpr"

    def __init__(self, op, left, right):
        self.op = op  # string operator
        self.left = left  # ExprNode
        self.right = right  # ExprNode


class LValueNode(ASTNode):
    """LValue (left value) node - variable reference"""
    node_name = "LValue"

    def __init__(self, name):
        self.name = name  # string


class NumberLiteralNode(ASTNode):
    """Number literal node"""
    node_name = "NumberLiteral"

    def __init__(self, value):
        self.value = int(value)  # integer value


class FuncCallNode(ASTNode):
    """Function call node"""
    node_name = "FuncCall"

    def __init__(self, name, args):
        self.name = name  # string
        self.args = args  # list of ExprNode


class UnaryMinusNode(ASTNode):
    """Unary minus expression node"""
    node_name = "UnaryMinus"

    def __init__(self, expr):
        self.expr = expr  # ExprNode