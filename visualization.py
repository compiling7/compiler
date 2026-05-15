"""AST visualization module for Rust-like language"""

from ast import *


class ASTVisualizer:
    """Visualizer for AST"""

    def __init__(self, ast):
        self.ast = ast

    def visualize(self):
        """Generate a visual representation of the AST (tree format)"""
        if self.ast is None:
            return "No AST to visualize"

        lines = []
        self._visualize_node(self.ast, "", True, lines)
        return "\n".join(lines)

    def _visualize_node(self, node, prefix, is_last, lines):
        """Recursively visualize a node and its children"""
        if node is None:
            return

        if isinstance(node, ASTNode):
            node_str = self._get_node_repr(node)
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{node_str}")

            children = self._get_children(node)
            child_prefix = prefix + ("    " if is_last else "│   ")

            for i, child in enumerate(children):
                is_child_last = (i == len(children) - 1)
                self._visualize_node(child, child_prefix, is_child_last, lines)
        else:
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{repr(node)}")

    def _get_node_repr(self, node):
        """Get a string representation of a node"""
        if isinstance(node, ProgramNode):
            return "Program"
        elif isinstance(node, FunctionDeclNode):
            return f"FunctionDecl: {node.name}"
        elif isinstance(node, ParamNode):
            return f"Param: {node.name} (mut={node.is_mutable})"
        elif isinstance(node, TypeNode):
            return f"Type: {node.type_name}"
        elif isinstance(node, BlockStmtNode):
            return f"Block (statements: {len(node.statements)})"
        elif isinstance(node, EmptyStmtNode):
            return "EmptyStmt"
        elif isinstance(node, ReturnStmtNode):
            return "ReturnStmt"
        elif isinstance(node, VarDeclStmtNode):
            mut_str = "mut " if node.is_mutable else ""
            return f"VarDecl: let {mut_str}{node.name}"
        elif isinstance(node, AssignStmtNode):
            return "AssignStmt"
        elif isinstance(node, ExprStmtNode):
            return "ExprStmt"
        elif isinstance(node, IfStmtNode):
            return "IfStmt"
        elif isinstance(node, WhileStmtNode):
            return "WhileStmt"
        elif isinstance(node, BinaryExprNode):
            return f"BinaryExpr: {node.op}"
        elif isinstance(node, LValueNode):
            return f"LValue: {node.name}"
        elif isinstance(node, NumberLiteralNode):
            return f"Number: {node.value}"
        elif isinstance(node, FuncCallNode):
            return f"FuncCall: {node.name}()"
        elif isinstance(node, UnaryMinusNode):
            return "UnaryMinus"
        else:
            return str(node.__class__.__name__)

    def _get_children(self, node):
        """Get child nodes for visualization"""
        children = []

        if isinstance(node, ProgramNode):
            children = node.declarations
        elif isinstance(node, FunctionDeclNode):
            children = [node.params, node.return_type, node.body]
            children = [c for c in children if c is not None]
        elif isinstance(node, ParamNode):
            children = [node.param_type]
        elif isinstance(node, BlockStmtNode):
            children = node.statements
        elif isinstance(node, ReturnStmtNode):
            if node.expr:
                children = [node.expr]
        elif isinstance(node, VarDeclStmtNode):
            if node.var_type:
                children.append(node.var_type)
            if node.init_expr:
                children.append(node.init_expr)
        elif isinstance(node, AssignStmtNode):
            children = [node.left, node.value]
        elif isinstance(node, ExprStmtNode):
            children = [node.expr]
        elif isinstance(node, IfStmtNode):
            children = [node.condition, node.then_block]
            if node.else_block:
                children.append(node.else_block)
        elif isinstance(node, WhileStmtNode):
            children = [node.condition, node.body]
        elif isinstance(node, BinaryExprNode):
            children = [node.left, node.right]
        elif isinstance(node, LValueNode):
            pass
        elif isinstance(node, NumberLiteralNode):
            pass
        elif isinstance(node, FuncCallNode):
            children = node.args
        elif isinstance(node, UnaryMinusNode):
            children = [node.expr]

        return children

    def format_structure(self):
        """Format AST as a structured syntax tree (like the example)"""
        if self.ast is None:
            return "No AST to format"

        lines = []
        self._build_structure(self.ast, "", lines)
        return "\n".join(lines)

    def _build_structure(self, node, indent, lines):
        """Build structured representation of the AST"""
        if node is None:
            return

        if isinstance(node, ProgramNode):
            lines.append(f"{indent}Program:")
            for decl in node.declarations:
                self._build_structure(decl, indent + "  ", lines)

        elif isinstance(node, FunctionDeclNode):
            ret_str = f" -> {node.return_type.type_name}" if node.return_type else ""
            lines.append(f"{indent}FunctionDeclaration(name='{node.name}', returns='{ret_str}')")
            lines.append(f"{indent}  Parameters:")
            if node.params:
                for p in node.params:
                    self._build_structure(p, indent + "    ", lines)
            else:
                lines.append(f"{indent}    (empty)")
            lines.append(f"{indent}  Body:")
            self._build_structure(node.body, indent + "    ", lines)

        elif isinstance(node, ParamNode):
            mut_str = "True" if node.is_mutable else "False"
            lines.append(f"{indent}Parameter(name='{node.name}', type='{node.param_type.type_name}', mutable={mut_str})")

        elif isinstance(node, TypeNode):
            lines.append(f"{indent}Type(value='{node.type_name}')")

        elif isinstance(node, BlockStmtNode):
            lines.append(f"{indent}Block:")
            for stmt in node.statements:
                self._build_structure(stmt, indent + "    ", lines)

        elif isinstance(node, EmptyStmtNode):
            lines.append(f"{indent}EmptyStatement")

        elif isinstance(node, ReturnStmtNode):
            lines.append(f"{indent}ReturnStatement:")
            if node.expr:
                self._build_structure(node.expr, indent + "    ", lines)
            else:
                lines.append(f"{indent}    (no value)")

        elif isinstance(node, VarDeclStmtNode):
            mut_str = "True" if node.is_mutable else "False"
            type_str = f", type=': {node.var_type.type_name}'" if node.var_type else ""
            lines.append(f"{indent}LetStatement(name='{node.name}', mutable={mut_str}{type_str})")
            if node.init_expr:
                lines.append(f"{indent}  Value:")
                self._build_structure(node.init_expr, indent + "    ", lines)

        elif isinstance(node, AssignStmtNode):
            lines.append(f"{indent}AssignmentStatement:")
            lines.append(f"{indent}  Left:")
            self._build_structure(node.left, indent + "    ", lines)
            lines.append(f"{indent}  Right:")
            self._build_structure(node.value, indent + "    ", lines)

        elif isinstance(node, ExprStmtNode):
            lines.append(f"{indent}ExpressionStatement:")
            self._build_structure(node.expr, indent + "    ", lines)

        elif isinstance(node, IfStmtNode):
            lines.append(f"{indent}IfStatement:")
            lines.append(f"{indent}  Condition:")
            self._build_structure(node.condition, indent + "    ", lines)
            lines.append(f"{indent}  Consequence:")
            self._build_structure(node.then_block, indent + "    ", lines)
            if node.else_block:
                lines.append(f"{indent}  Alternative:")
                self._build_structure(node.else_block, indent + "    ", lines)

        elif isinstance(node, WhileStmtNode):
            lines.append(f"{indent}WhileStatement:")
            lines.append(f"{indent}  Condition:")
            self._build_structure(node.condition, indent + "    ", lines)
            lines.append(f"{indent}  Body:")
            self._build_structure(node.body, indent + "    ", lines)

        elif isinstance(node, BinaryExprNode):
            lines.append(f"{indent}InfixExpression(operator='{node.op}')")
            lines.append(f"{indent}  Left:")
            self._build_structure(node.left, indent + "    ", lines)
            lines.append(f"{indent}  Right:")
            self._build_structure(node.right, indent + "    ", lines)

        elif isinstance(node, LValueNode):
            lines.append(f"{indent}Identifier(value='{node.name}')")

        elif isinstance(node, NumberLiteralNode):
            lines.append(f"{indent}IntegerLiteral(value={node.value})")

        elif isinstance(node, FuncCallNode):
            lines.append(f"{indent}FunctionCall(name='{node.name}')")
            lines.append(f"{indent}  Arguments:")
            for arg in node.args:
                self._build_structure(arg, indent + "    ", lines)

        elif isinstance(node, UnaryMinusNode):
            lines.append(f"{indent}UnaryMinus:")
            self._build_structure(node.expr, indent + "    ", lines)

        else:
            lines.append(f"{indent}{node.__class__.__name__}")

    def to_tree_string(self):
        """Alternative tree representation"""
        if self.ast is None:
            return "No AST"

        result = []
        self._build_tree_string(self.ast, "", result)
        return "\n".join(result)

    def _build_tree_string(self, node, indent, result):
        """Build tree string with more detail"""
        if isinstance(node, ASTNode):
            node_repr = self._get_node_repr(node)
            result.append(f"{indent}{node_repr}")

            children = self._get_children(node)
            for i, child in enumerate(children):
                child_indent = indent + ("  " if i == len(children) - 1 else "├── ")
                if not isinstance(child, ASTNode):
                    result.append(f"{child_indent}{child}")
                else:
                    self._build_tree_string(child, child_indent, result)


def format_ast(ast):
    """Format an AST for display (tree format)"""
    if ast is None:
        return "无法解析的语法树"

    viz = ASTVisualizer(ast)
    return viz.visualize()


def format_ast_tree(ast):
    """Format an AST as a tree with more details"""
    if ast is None:
        return "无法解析的语法树"

    viz = ASTVisualizer(ast)
    return viz.to_tree_string()


def format_syntax_structure(ast):
    """Format an AST as a structured syntax tree"""
    if ast is None:
        return "无法解析的语法树"

    viz = ASTVisualizer(ast)
    return viz.format_structure()