"""Rust-like language parser using recursive descent"""

from lexer import Lexer
from ast import *
from token_types import *


class Parser:
    """Recursive descent parser for Rust-like language"""

    def __init__(self, source_code):
        self.lexer = Lexer(source_code)
        self.tokens = []
        self.pos = 0
        self.errors = []

    def parse(self):
        """Parse the source code and return the AST"""
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
        """Get the current token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF token

    def peek_token(self, offset=1):
        """Look at a token without consuming it"""
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return self.tokens[-1]

    def advance(self):
        """Consume the current token and move to the next"""
        self.pos += 1

    def expect(self, token_type):
        """Expect a token of the given type and consume it"""
        token = self.current_token()
        if token.type != token_type:
            raise Exception(f"第{token.line}行第{token.column}列: 期望 '{token_type}'，实际是 '{token.type}'")
        self.advance()
        return token

    def parse_program(self):
        """Program -> Declaration串
        Declaration串 -> 空 | Declaration Declaration串
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
        """FunctionDecl -> FunctionHeader Block
        FunctionHeader -> fn ID ( ParameterList ) ReturnType?
        """
        self.expect(TT_KEYWORD_FN)
        name_token = self.expect(TT_ID)
        self.expect(TT_LPAREN)

        params = self.parse_parameter_list()

        self.expect(TT_RPAREN)

        # Check for return type
        return_type = None
        if self.current_token().type == TT_ARROW:
            self.advance()
            return_type = self.parse_type()

        body = self.parse_block()
        return FunctionDeclNode(name_token.value, params, return_type, body)

    def parse_parameter_list(self):
        """ParameterList -> 空 | Param, ParameterList
        Param -> VariableAttribute ID : Type
        """
        params = []

        # Check if list is empty
        if self.current_token().type == TT_RPAREN:
            return params

        # Parse first parameter
        param = self.parse_parameter()
        params.append(param)

        # Parse remaining parameters
        while self.current_token().type == TT_COMMA:
            self.advance()
            param = self.parse_parameter()
            params.append(param)

        return params

    def parse_parameter(self):
        """Param -> VariableAttribute ID : Type"""
        is_mutable = False

        # Check for mut
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
        """Block -> { Statement串 }
        Statement串 -> 空 | Statement Statement串
        """
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
        """Statement -> ; | ReturnStmt | VarDeclStmt | AssignStmt | ExprStmt | IfStmt | WhileStmt"""
        token = self.current_token()

        # Empty statement
        if token.type == TT_SEMICOLON:
            self.advance()
            return EmptyStmtNode()

        # Return statement
        if token.type == TT_KEYWORD_RETURN:
            return self.parse_return_stmt()

        # Variable declaration
        if token.type == TT_KEYWORD_LET:
            return self.parse_var_decl_stmt()

        # If statement
        if token.type == TT_KEYWORD_IF:
            return self.parse_if_stmt()

        # While statement
        if token.type == TT_KEYWORD_WHILE:
            return self.parse_while_stmt()

        # Try to parse as expression statement
        expr = self.try_parse_expression()
        if expr:
            self.expect(TT_SEMICOLON)
            return ExprStmtNode(expr)

        # Unknown statement
        raise Exception(f"第{token.line}行第{token.column}列: 未知语句开头 '{token.value}'")

    def parse_return_stmt(self):
        """ReturnStmt -> return ; | return Expression ;"""
        self.expect(TT_KEYWORD_RETURN)

        # Check if there's an expression
        if self.current_token().type == TT_SEMICOLON:
            self.advance()
            return ReturnStmtNode(None)

        expr = self.parse_expression()
        self.expect(TT_SEMICOLON)
        return ReturnStmtNode(expr)

    def parse_var_decl_stmt(self):
        """VarDeclStmt -> let VariableAttribute ID (: Type)? (= Expression)? ;"""
        self.expect(TT_KEYWORD_LET)

        is_mutable = False
        if self.current_token().type == TT_KEYWORD_MUT:
            is_mutable = True
            self.advance()

        name_token = self.expect(TT_ID)

        var_type = None
        if self.current_token().type == TT_COLON:
            self.advance()
            var_type = self.parse_type()

        init_expr = None
        if self.current_token().type == TT_ASSIGN:
            self.advance()
            init_expr = self.parse_expression()

        self.expect(TT_SEMICOLON)
        return VarDeclStmtNode(name_token.value, is_mutable, var_type, init_expr)

    def parse_if_stmt(self):
        """IfStmt -> if Expression Block ElsePart
        ElsePart -> 空 | else Block | else IfStmt
        """
        self.expect(TT_KEYWORD_IF)

        condition = self.parse_expression()
        then_block = self.parse_block()

        else_block = None
        if self.current_token().type == TT_KEYWORD_ELSE:
            self.advance()
            if self.current_token().type == TT_KEYWORD_IF:
                else_block = self.parse_if_stmt()
            else:
                else_block = self.parse_block()

        return IfStmtNode(condition, then_block, else_block)

    def parse_while_stmt(self):
        """WhileStmt -> while Expression Block"""
        self.expect(TT_KEYWORD_WHILE)

        condition = self.parse_expression()
        body = self.parse_block()

        return WhileStmtNode(condition, body)

    def try_parse_expression(self):
        """Try to parse an expression (for assignment statements)"""
        # Check if starts with an identifier (potential left value or expression)
        token = self.current_token()

        if token.type == TT_ID:
            # Look ahead: ID = ... -> assignment
            # Look ahead: ID ( ... ) -> function call
            # Look ahead: ID ; or other -> simple expression
            next_token = self.peek_token()

            if next_token.type == TT_ASSIGN:
                # Assignment statement: LValue = Expression
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
        """AdditiveExpr -> Term (AddOp Term)*
        AddOp -> + | -
        """
        left = self.parse_term()

        while self.current_token().type in [TT_PLUS, TT_MINUS]:
            op = self.current_token().value
            self.advance()
            right = self.parse_term()
            left = BinaryExprNode(op, left, right)

        return left

    def parse_term(self):
        """Term -> Factor (MulOp Factor)*
        MulOp -> * | /
        """
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

        # Number literal
        if token.type == TT_NUM:
            self.advance()
            return NumberLiteralNode(token.value)

        # Parenthesized expression
        if token.type == TT_LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TT_RPAREN)
            return expr

        # Unary minus
        if token.type == TT_MINUS:
            self.advance()
            factor = self.parse_factor()
            return UnaryMinusNode(factor)

        # Function call or simple identifier
        if token.type == TT_ID:
            name = token.value
            self.advance()

            # Check for function call
            if self.current_token().type == TT_LPAREN:
                self.advance()
                args = self.parse_argument_list()
                self.expect(TT_RPAREN)
                return FuncCallNode(name, args)

            # Simple identifier as expression (treated as lvalue)
            return LValueNode(name)

        # Unknown factor
        raise Exception(f"第{token.line}行第{token.column}列: 期望表达式，实际是 '{token.type}'")

    def parse_argument_list(self):
        """ArgumentList -> 空 | Expression ( , Expression )*"""
        args = []

        if self.current_token().type == TT_RPAREN:
            return args

        # Parse first argument
        expr = self.parse_expression()
        args.append(expr)

        # Parse remaining arguments
        while self.current_token().type == TT_COMMA:
            self.advance()
            expr = self.parse_expression()
            args.append(expr)

        return args