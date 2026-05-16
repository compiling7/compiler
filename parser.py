"""Rust 类语言语法分析器 - 递归下降分析"""

from lexer import Lexer
from ast import *
from token_types import *


class Parser:
    """Rust 类语言递归下降语法分析器"""

    def __init__(self, source_code: str):
        self.lexer = Lexer(source_code)
        self.tokens = []  # Token 序列
        self.pos = 0     # 当前解析位置
        self.errors = []  # 错误信息列表

    def parse(self) -> tuple:
        """解析源代码，返回 (AST, 错误列表)"""
        self.tokens = self.lexer.tokenize()
        self.pos = 0
        self.errors = []

        try:
            program = self.parse_program()
            if self.errors:
                return None, self.errors
            return program, []
        except Exception as e:
            self.errors.append(str(e))
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
        self.pos += 1

    def expect(self, token_type):
        """期望并消费指定类型的 Token"""
        token = self.current_token()
        if token.type != token_type:
            raise Exception(f"第{token.line}行第{token.column}列: 期望 '{token_type}'，实际是 '{token.type}'")
        self.advance()
        return token

    def parse_program(self):
        """Program -> Declaration*
        Declaration -> FunctionDecl
        """
        declarations = []
        while self.current_token().type != TT_EOF:
            decl = self.parse_declaration()
            if decl:
                declarations.append(decl)
        return ProgramNode(declarations)

    def parse_declaration(self):
        """Declaration -> FunctionDecl"""
        return self.parse_function_decl()

    def parse_function_decl(self):
        """FunctionDecl -> fn ID ( ParameterList ) ReturnType? Block"""
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
        return FunctionDeclNode(name_token.value, params, return_type, body)

    def parse_parameter_list(self):
        """ParameterList -> ε | Param (, Param)*"""
        params = []

        # 检查是否为空列表
        if self.current_token().type == TT_RPAREN:
            return params

        # 解析第一个参数
        param = self.parse_parameter()
        params.append(param)

        # 解析剩余参数
        while self.current_token().type == TT_COMMA:
            self.advance()
            param = self.parse_parameter()
            params.append(param)

        return params

    def parse_parameter(self):
        """Param -> mut? ID : Type"""
        is_mutable = False

        # 检查 mut 关键字
        if self.current_token().type == TT_KEYWORD_MUT:
            is_mutable = True
            self.advance()

        name_token = self.expect(TT_ID)
        self.expect(TT_COLON)
        param_type = self.parse_type()

        return ParamNode(name_token.value, is_mutable, param_type)

    def parse_type(self):
        """Type -> i32"""
        type_token = self.expect(TT_KEYWORD_I32)
        return TypeNode(type_token.value)

    def parse_block(self):
        """Block -> { Statement* }"""
        self.expect(TT_LBRACE)

        statements = []
        while self.current_token().type != TT_RBRACE:
            if self.current_token().type == TT_EOF:
                raise Exception("缺少 '}'")
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        self.expect(TT_RBRACE)
        return BlockStmtNode(statements)

    def parse_statement(self):
        """Statement -> ; | return | let | if | while | Expr"""
        token = self.current_token()

        # 空语句
        if token.type == TT_SEMICOLON:
            self.advance()
            return EmptyStmtNode()

        # return 语句
        if token.type == TT_KEYWORD_RETURN:
            return self.parse_return_stmt()

        # let 变量声明
        if token.type == TT_KEYWORD_LET:
            return self.parse_var_decl_stmt()

        # if 条件语句
        if token.type == TT_KEYWORD_IF:
            return self.parse_if_stmt()

        # while 循环语句
        if token.type == TT_KEYWORD_WHILE:
            return self.parse_while_stmt()

        # 尝试解析为表达式语句或赋值语句
        expr = self.try_parse_expression()
        if expr:
            self.expect(TT_SEMICOLON)
            return ExprStmtNode(expr)

        # 未知语句
        raise Exception(f"第{token.line}行第{token.column}列: 未知语句开头 '{token.value}'")

    def parse_return_stmt(self):
        """ReturnStmt -> return Expression? ;"""
        self.expect(TT_KEYWORD_RETURN)

        # 检查是否有表达式
        if self.current_token().type == TT_SEMICOLON:
            self.advance()
            return ReturnStmtNode(None)

        expr = self.parse_expression()
        self.expect(TT_SEMICOLON)
        return ReturnStmtNode(expr)

    def parse_var_decl_stmt(self):
        """VarDeclStmt -> let mut? ID (: Type)? (= Expression)? ;"""
        self.expect(TT_KEYWORD_LET)

        is_mutable = False
        if self.current_token().type == TT_KEYWORD_MUT:
            is_mutable = True
            self.advance()

        name_token = self.expect(TT_ID)

        # 类型注解
        var_type = None
        if self.current_token().type == TT_COLON:
            self.advance()
            var_type = self.parse_type()

        # 初始化表达式
        init_expr = None
        if self.current_token().type == TT_ASSIGN:
            self.advance()
            init_expr = self.parse_expression()

        self.expect(TT_SEMICOLON)
        return VarDeclStmtNode(name_token.value, is_mutable, var_type, init_expr)

    def parse_if_stmt(self):
        """IfStmt -> if Expression Block (else Block | IfStmt)?"""
        self.expect(TT_KEYWORD_IF)

        condition = self.parse_expression()
        then_block = self.parse_block()

        else_block = None
        if self.current_token().type == TT_KEYWORD_ELSE:
            self.advance()
            if self.current_token().type == TT_KEYWORD_IF:
                # else if: 递归调用自身
                else_block = self.parse_if_stmt()
            else:
                # else Block
                else_block = self.parse_block()

        return IfStmtNode(condition, then_block, else_block)

    def parse_while_stmt(self):
        """WhileStmt -> while Expression Block"""
        self.expect(TT_KEYWORD_WHILE)

        condition = self.parse_expression()
        body = self.parse_block()

        return WhileStmtNode(condition, body)

    def try_parse_expression(self):
        """尝试解析表达式或赋值语句"""
        token = self.current_token()

        if token.type == TT_ID:
            # 向前看一个 Token 判断是赋值还是表达式
            next_token = self.peek_token()

            if next_token.type == TT_ASSIGN:
                # 赋值语句: id = expr
                self.advance()
                left = LValueNode(token.value)
                self.advance()  # consume =
                value = self.parse_expression()
                return AssignStmtNode(left, value)

        return self.parse_expression()

    def parse_expression(self):
        """Expression -> AdditiveExpr (ComparisonOp AdditiveExpr)*
        ComparisonOp -> < | <= | > | >= | == | !=
        """
        left = self.parse_additive_expr()

        while self.current_token().type in [TT_LT, TT_LE, TT_GT, TT_GE, TT_EQ, TT_NE]:
            op = self.current_token().value
            self.advance()
            right = self.parse_additive_expr()
            left = BinaryExprNode(op, left, right)

        return left

    def parse_additive_expr(self):
        """AdditiveExpr -> Term (('+' | '-') Term)*"""
        left = self.parse_term()

        while self.current_token().type in [TT_PLUS, TT_MINUS]:
            op = self.current_token().value
            self.advance()
            right = self.parse_term()
            left = BinaryExprNode(op, left, right)

        return left

    def parse_term(self):
        """Term -> Factor (('*' | '/') Factor)*"""
        left = self.parse_factor()

        while self.current_token().type in [TT_MUL, TT_DIV]:
            op = self.current_token().value
            self.advance()
            right = self.parse_factor()
            left = BinaryExprNode(op, left, right)

        return left

    def parse_factor(self):
        """Factor -> NUM | ID ( ArgumentList )? | ( Expression ) | - Factor"""
        token = self.current_token()

        # 数字字面量
        if token.type == TT_NUM:
            self.advance()
            return NumberLiteralNode(token.value)

        # 括号表达式
        if token.type == TT_LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TT_RPAREN)
            return expr

        # 一元负号
        if token.type == TT_MINUS:
            self.advance()
            factor = self.parse_factor()
            return UnaryMinusNode(factor)

        # 函数调用或标识符
        if token.type == TT_ID:
            name = token.value
            self.advance()

            # 检查函数调用
            if self.current_token().type == TT_LPAREN:
                self.advance()
                args = self.parse_argument_list()
                self.expect(TT_RPAREN)
                return FuncCallNode(name, args)

            # 标识符作为左值
            return LValueNode(name)

        # 未知因子
        raise Exception(f"第{token.line}行第{token.column}列: 期望表达式，实际是 '{token.type}'")

    def parse_argument_list(self):
        """ArgumentList -> ε | Expression (, Expression)*"""
        args = []

        if self.current_token().type == TT_RPAREN:
            return args

        # 解析第一个实参
        expr = self.parse_expression()
        args.append(expr)

        # 解析剩余实参
        while self.current_token().type == TT_COMMA:
            self.advance()
            expr = self.parse_expression()
            args.append(expr)

        return args