"""Rust 类语言语法分析器 - 递归下降分析"""

from lexer import Lexer
from ast import *
from token_types import *


class Parser:
    """Rust 类语言递归下降语法分析器"""

    def __init__(self, source_code: str, tracer=None):
        self.lexer = Lexer(source_code)
        self.tokens = []  # Token 序列
        self.pos = 0     # 当前解析位置
        self.errors = []  # 错误信息列表
        self.tracer = tracer  # 可选的 ParserTracer 用于过程可视化

    def parse(self) -> tuple:
        """解析源代码，返回 (AST, 错误列表)"""
        self.tokens = self.lexer.tokenize()
        self.pos = 0
        self.errors = []

        if self.tracer:
            self.tracer.begin(self.tokens)

        try:
            program = self.parse_program()
            if self.errors:
                if self.tracer:
                    self.tracer.end(None, self.errors)
                return None, self.errors
            if self.tracer:
                self.tracer.end(program, [])
            return program, []
        except Exception as e:
            self.errors.append(str(e))
            if self.tracer:
                self.tracer.end(None, self.errors)
            return None, self.errors

    def current_token(self):
        """获取当前 Token（不消费）"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF token

    def peek_token(self, offset=1):
        """向前查看 Token（不消费）"""
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return self.tokens[-1]

    def advance(self):
        """消费当前 Token，移动到下一个"""
        token = self.current_token()
        self.pos += 1
        if self.tracer:
            self.tracer.consume(token, self.pos - 1)

    def expect(self, token_type):
        """期望并消费指定类型的 Token"""
        token = self.current_token()
        if token.type != token_type:
            msg = f"第{token.line}行第{token.column}列: 期望 '{token_type}'，实际是 '{token.type}'"
            if self.tracer:
                self.tracer.error(msg, token, self.pos)
            raise Exception(msg)
        self.advance()
        return token

    def _trace_enter(self, func_name, rule=""):
        if self.tracer:
            self.tracer.enter(func_name, rule, self.current_token(), self.pos)

    def _trace_exit(self, func_name, result):
        if self.tracer:
            self.tracer.exit(func_name, result, self.pos)

    def parse_program(self):
        """Program -> Declaration*
        Declaration -> FunctionDecl
        """
        self._trace_enter("parse_program", "Program → Declaration*")
        declarations = []
        while self.current_token().type != TT_EOF:
            decl = self.parse_declaration()
            if decl:
                declarations.append(decl)
        result = ProgramNode(declarations)
        self._trace_exit("parse_program", result)
        return result

    def parse_declaration(self):
        """Declaration -> FunctionDecl"""
        self._trace_enter("parse_declaration", "Declaration → FunctionDecl")
        result = self.parse_function_decl()
        self._trace_exit("parse_declaration", result)
        return result

    def parse_function_decl(self):
        """FunctionDecl -> fn ID ( ParameterList ) ReturnType? Block"""
        self._trace_enter("parse_function_decl", "FunctionDecl → fn ID (Params?) →Type? Block")
        self.expect(TT_KEYWORD_FN)
        name_token = self.expect(TT_ID)
        self.expect(TT_LPAREN)

        params = self.parse_parameter_list()

        self.expect(TT_RPAREN)

        # 检查返回值类型
        return_type = None
        if self.current_token().type == TT_ARROW:
            self.advance()
            return_type = self.parse_type()

        body = self.parse_block()
        result = FunctionDeclNode(name_token.value, params, return_type, body)
        self._trace_exit("parse_function_decl", result)
        return result

    def parse_parameter_list(self):
        """ParameterList -> ε | Param (, Param)*"""
        self._trace_enter("parse_parameter_list", "ParameterList → ε | Param (, Param)*")
        params = []
        # 检查是否为空列表
        if self.current_token().type == TT_RPAREN:
            self._trace_exit("parse_parameter_list", params)
            return params
        param = self.parse_parameter()
        params.append(param)
        while self.current_token().type == TT_COMMA:
            self.advance()
            param = self.parse_parameter()
            params.append(param)
        self._trace_exit("parse_parameter_list", params)
        return params

    def parse_parameter(self):
        """Param -> mut? ID : Type"""
        self._trace_enter("parse_parameter", "Param → mut? ID : Type")
        is_mutable = False
        if self.current_token().type == TT_KEYWORD_MUT:
            is_mutable = True
            self.advance()
        name_token = self.expect(TT_ID)
        self.expect(TT_COLON)
        param_type = self.parse_type()
        result = ParamNode(name_token.value, is_mutable, param_type)
        self._trace_exit("parse_parameter", result)
        return result

    def parse_type(self):
        """Type -> i32 | [ Type ; NUM ]"""
        self._trace_enter("parse_type", "Type → i32 | [ Type ; NUM ]")
        if self.current_token().type == TT_LBRACKET:
            self.advance()
            elem_type = self.parse_type()
            self.expect(TT_SEMICOLON)
            size_token = self.expect(TT_NUM)
            self.expect(TT_RBRACKET)
            result = ArrayTypeNode(elem_type, int(size_token.value))
            self._trace_exit("parse_type", result)
            return result
        type_token = self.expect(TT_KEYWORD_I32)
        result = TypeNode(type_token.value)
        self._trace_exit("parse_type", result)
        return result

    def parse_block(self):
        """Block -> { Statement* }"""
        self._trace_enter("parse_block", "Block → { Statement* }")
        self.expect(TT_LBRACE)
        statements = []
        while self.current_token().type != TT_RBRACE:
            if self.current_token().type == TT_EOF:
                raise Exception("缺少 '}'")
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        self.expect(TT_RBRACE)
        result = BlockStmtNode(statements)
        self._trace_exit("parse_block", result)
        return result

    def parse_statement(self):
        """Statement -> ; | return | let | if | while | for | ID = Expr | Expr"""
        self._trace_enter("parse_statement", "Statement → ε | return | let | if | while | for | ID = Expr | Expr")
        token = self.current_token()
        if token.type == TT_SEMICOLON:
            self.advance()
            result = EmptyStmtNode()
            self._trace_exit("parse_statement", result)
            return result
        if token.type == TT_KEYWORD_RETURN:
            result = self.parse_return_stmt()
            self._trace_exit("parse_statement", result)
            return result
        if token.type == TT_KEYWORD_LET:
            result = self.parse_var_decl_stmt()
            self._trace_exit("parse_statement", result)
            return result
        if token.type == TT_KEYWORD_IF:
            result = self.parse_if_stmt()
            self._trace_exit("parse_statement", result)
            return result
        if token.type == TT_KEYWORD_WHILE:
            result = self.parse_while_stmt()
            self._trace_exit("parse_statement", result)
            return result
        if token.type == TT_KEYWORD_FOR:
            result = self.parse_for_stmt()
            self._trace_exit("parse_statement", result)
            return result
        expr = self.try_parse_expression()
        if expr:
            self.expect(TT_SEMICOLON)
            result = ExprStmtNode(expr)
            self._trace_exit("parse_statement", result)
            return result
        raise Exception(f"第{token.line}行第{token.column}列: 未知语句开头 '{token.value}'")

    def parse_return_stmt(self):
        """ReturnStmt -> return Expression? ;"""
        self._trace_enter("parse_return_stmt", "ReturnStmt → return Expression? ;")
        self.expect(TT_KEYWORD_RETURN)
        if self.current_token().type == TT_SEMICOLON:
            self.advance()
            result = ReturnStmtNode(None)
            self._trace_exit("parse_return_stmt", result)
            return result
        expr = self.parse_expression()
        self.expect(TT_SEMICOLON)
        result = ReturnStmtNode(expr)
        self._trace_exit("parse_return_stmt", result)
        return result

    def parse_var_decl(self):
        """VariableDecl -> mut? ID (: Type)?"""
        self._trace_enter("parse_var_decl", "VarDecl → mut? ID (: Type)?")
        is_mutable = False
        if self.current_token().type == TT_KEYWORD_MUT:
            is_mutable = True
            self.advance()
        name_token = self.expect(TT_ID)
        var_type = None
        if self.current_token().type == TT_COLON:
            self.advance()
            var_type = self.parse_type()
        result = (name_token.value, is_mutable, var_type)
        self._trace_exit("parse_var_decl", result)
        return result

    def parse_var_decl_stmt(self):
        """VarDeclStmt -> let VarDecl (= Expression)? ;"""
        self._trace_enter("parse_var_decl_stmt", "VarDeclStmt → let VarDecl (= Expr)? ;")
        self.expect(TT_KEYWORD_LET)
        name, is_mutable, var_type = self.parse_var_decl()
        if self.current_token().type == TT_ASSIGN:
            self.advance()
            init_expr = self.parse_expression()
            self.expect(TT_SEMICOLON)
            result = VarDeclStmtNode(name, is_mutable, var_type, init_expr)
            self._trace_exit("parse_var_decl_stmt", result)
            return result
        self.expect(TT_SEMICOLON)
        result = VarDeclStmtNode(name, is_mutable, var_type, None)
        self._trace_exit("parse_var_decl_stmt", result)
        return result

    def parse_if_stmt(self):
        """IfStmt -> if Expression Block ElsePart?"""
        self._trace_enter("parse_if_stmt", "IfStmt → if Expr Block (else Block)?")
        self.expect(TT_KEYWORD_IF)
        condition = self.parse_expression()
        then_block = self.parse_block()
        else_block = None
        if self.current_token().type == TT_KEYWORD_ELSE:
            else_block = self.parse_else_part()
        result = IfStmtNode(condition, then_block, else_block)
        self._trace_exit("parse_if_stmt", result)
        return result

    def parse_else_part(self):
        """ElsePart -> else Block | else if Expression Block ElsePart?"""
        self._trace_enter("parse_else_part", "ElsePart → else Block | else if Expr Block")
        self.expect(TT_KEYWORD_ELSE)
        if self.current_token().type == TT_KEYWORD_IF:
            self.advance()
            condition = self.parse_expression()
            then_block = self.parse_block()
            else_part = None
            if self.current_token().type == TT_KEYWORD_ELSE:
                else_part = self.parse_else_part()
            result = IfStmtNode(condition, then_block, else_part)
            self._trace_exit("parse_else_part", result)
            return result
        result = self.parse_block()
        self._trace_exit("parse_else_part", result)
        return result

    def parse_while_stmt(self):
        """WhileStmt -> while Expression Block"""
        self._trace_enter("parse_while_stmt", "WhileStmt → while Expr Block")
        self.expect(TT_KEYWORD_WHILE)
        condition = self.parse_expression()
        body = self.parse_block()
        result = WhileStmtNode(condition, body)
        self._trace_exit("parse_while_stmt", result)
        return result

    def parse_for_stmt(self):
        """ForStmt -> for VarDecl in Iterable Block"""
        self._trace_enter("parse_for_stmt", "ForStmt → for VarDecl in Iterable Block")
        self.expect(TT_KEYWORD_FOR)
        name, is_mutable, _ = self.parse_var_decl()
        self.expect(TT_KEYWORD_IN)
        iterable = self.parse_iterable()
        body = self.parse_block()
        result = ForStmtNode(name, is_mutable, iterable, body)
        self._trace_exit("parse_for_stmt", result)
        return result

    def parse_iterable(self):
        """Iterable -> Expression .. Expression | Expression"""
        self._trace_enter("parse_iterable", "Iterable → Expr .. Expr | Expr")
        start = self.parse_expression()
        if self.current_token().type == TT_DOTDOT:
            self.advance()
            end = self.parse_expression()
            result = RangeNode(start, end)
            self._trace_exit("parse_iterable", result)
            return result
        self._trace_exit("parse_iterable", start)
        return start

    def try_parse_expression(self):
        """尝试解析表达式或赋值语句"""
        self._trace_enter("try_parse_expression", "ExprOrAssign → ID = Expr | Expr")
        token = self.current_token()
        if token.type == TT_ID:
            next_token = self.peek_token()
            if next_token.type == TT_ASSIGN:
                self.advance()
                left = LValueNode(token.value)
                self.advance()  # consume =
                value = self.parse_expression()
                result = AssignStmtNode(left, value)
                self._trace_exit("try_parse_expression", result)
                return result
        result = self.parse_expression()
        self._trace_exit("try_parse_expression", result)
        return result

    def parse_expression(self):
        """Expression -> AdditiveExpr (ComparisonOp AdditiveExpr)*"""
        self._trace_enter("parse_expression", "Expr → AdditiveExpr (CompareOp AdditiveExpr)*")
        left = self.parse_additive_expr()
        while self.current_token().type in [TT_LT, TT_LE, TT_GT, TT_GE, TT_EQ, TT_NE]:
            op = self.current_token().value
            self.advance()
            right = self.parse_additive_expr()
            left = BinaryExprNode(op, left, right)
        self._trace_exit("parse_expression", left)
        return left

    def parse_additive_expr(self):
        """AdditiveExpr -> Term (('+' | '-') Term)*"""
        self._trace_enter("parse_additive_expr", "AdditiveExpr → Term ((+|-) Term)*")
        left = self.parse_term()
        while self.current_token().type in [TT_PLUS, TT_MINUS]:
            op = self.current_token().value
            self.advance()
            right = self.parse_term()
            left = BinaryExprNode(op, left, right)
        self._trace_exit("parse_additive_expr", left)
        return left

    def parse_term(self):
        """Term -> Factor (('*' | '/') Factor)*"""
        self._trace_enter("parse_term", "Term → Factor ((*|/) Factor)*")
        left = self.parse_factor()
        while self.current_token().type in [TT_MUL, TT_DIV]:
            op = self.current_token().value
            self.advance()
            right = self.parse_factor()
            left = BinaryExprNode(op, left, right)
        self._trace_exit("parse_term", left)
        return left

    def parse_factor(self):
        """Factor -> NUM | Accessor | ( Expression ) | - Factor"""
        self._trace_enter("parse_factor", "Factor → NUM | Accessor | (Expr) | -Factor")
        token = self.current_token()
        if token.type == TT_NUM:
            self.advance()
            result = NumberLiteralNode(token.value)
            self._trace_exit("parse_factor", result)
            return result
        if token.type == TT_LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TT_RPAREN)
            self._trace_exit("parse_factor", expr)
            return expr
        if token.type == TT_MINUS:
            self.advance()
            factor = self.parse_factor()
            result = UnaryMinusNode(factor)
            self._trace_exit("parse_factor", result)
            return result
        if token.type == TT_ID or token.type == TT_LBRACKET:
            result = self.parse_accessor()
            self._trace_exit("parse_factor", result)
            return result
        raise Exception(f"第{token.line}行第{token.column}列: 期望表达式，实际是 '{token.type}'")

    def parse_accessor(self):
        """Accessor -> [ ElementList ] | ID ( ArgumentList )? ( [ Expression ] )*"""
        self._trace_enter("parse_accessor", "Accessor → [Elements] | ID (Args)? ([Expr])*")
        if self.current_token().type == TT_LBRACKET:
            result = self.parse_array_literal()
            self._trace_exit("parse_accessor", result)
            return result
        name_token = self.expect(TT_ID)
        if self.current_token().type == TT_LPAREN:
            self.advance()
            args = self.parse_argument_list()
            self.expect(TT_RPAREN)
            result = FuncCallNode(name_token.value, args)
        else:
            result = LValueNode(name_token.value)
        while self.current_token().type == TT_LBRACKET:
            self.advance()
            index = self.parse_expression()
            self.expect(TT_RBRACKET)
            result = ArrayAccessNode(result, index)
        self._trace_exit("parse_accessor", result)
        return result

    def parse_array_literal(self):
        """ArrayLiteral -> [ ElementList ]"""
        self._trace_enter("parse_array_literal", "ArrayLiteral → [ Expr (, Expr)* ]")
        self.expect(TT_LBRACKET)
        elements = []
        if self.current_token().type != TT_RBRACKET:
            expr = self.parse_expression()
            elements.append(expr)
            while self.current_token().type == TT_COMMA:
                self.advance()
                if self.current_token().type == TT_RBRACKET:
                    break
                expr = self.parse_expression()
                elements.append(expr)
        self.expect(TT_RBRACKET)
        result = ArrayLiteralNode(elements)
        self._trace_exit("parse_array_literal", result)
        return result

    def parse_argument_list(self):
        """ArgumentList -> ε | Expression (, Expression)*"""
        self._trace_enter("parse_argument_list", "ArgList → ε | Expr (, Expr)*")
        args = []
        if self.current_token().type == TT_RPAREN:
            self._trace_exit("parse_argument_list", args)
            return args
        expr = self.parse_expression()
        args.append(expr)
        while self.current_token().type == TT_COMMA:
            self.advance()
            expr = self.parse_expression()
            args.append(expr)
        self._trace_exit("parse_argument_list", args)
        return args