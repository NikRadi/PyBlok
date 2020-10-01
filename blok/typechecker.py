from enum import Enum
from blok.token import Token, TokenKind
from blok.astnodes import (
    BlkProgram,
    ReturnStatement,
    FuncCall,
    FuncDecl,
    Block,
    ForLoop,
    WhileLoop,
    LoopControl,
    LoopControlKind,
    IfStatement,
    VarAssign,
    VarDecl,
    Literal,
    UnaryOp,
    BinaryOp
)


class TypeChecker:
    def __init__(self, ast):
        print(ast)
        self.funcident_to_evalkind = {}
        self.structident_to_stacksize = {}
        self.current_func = None
        self.typecheck_blkprogram(ast)
        print(ast)

    def typecheck_blkprogram(self, blkprogram):
        for funcdecl in blkprogram.funcdecls:
            ident = funcdecl.ident.value
            if funcdecl.return_token.kind == TokenKind.VOID:
                self.funcident_to_evalkind[ident] = EvalKind.VOID
            elif funcdecl.return_token.kind == TokenKind.INT:
                self.funcident_to_evalkind[ident] = EvalKind.INT
            else: assert False, f"\n{ident}"

        for struct in blkprogram.structs:
            self.typecheck_struct(struct)

        for funcdecl in blkprogram.funcdecls:
            self.typecheck_funcdecl(funcdecl)

    def typecheck_struct(self, struct):
        ident = struct.ident.value
        self.structident_to_stacksize[ident] = struct.stack_size

    def typecheck_return_statement(self, return_statement):
        if return_statement.expr != None:
            self.typecheck_expr(return_statement.expr)

    def typecheck_funccall(self, funccall):
        ident = funccall.ident.value
        funccall.eval_kind = self.funcident_to_evalkind[ident]
        for arg in funccall.args:
            self.typecheck_expr(arg)

    def typecheck_funcdecl(self, funcdecl):
        self.current_func = funcdecl
        funcdecl.stack_size = len(funcdecl.params)

        self.typecheck_block(funcdecl.block)
        if funcdecl.return_token.kind == TokenKind.VOID and \
           (len(funcdecl.block.statements) == 0 or
            not isinstance(funcdecl.block.statements[-1], ReturnStatement)):
            funcdecl.block.statements.append(ReturnStatement())

    def typecheck_block(self, block):
        for statement in block.statements:
            if isinstance(statement, VarDecl):
                self.typecheck_vardecl(statement)
            elif isinstance(statement, VarAssign):
                self.typecheck_varassign(statement)
            elif isinstance(statement, IfStatement):
                self.typecheck_if_statement(statement)
            elif isinstance(statement, WhileLoop):
                self.typecheck_while_loop(statement)
            elif isinstance(statement, ForLoop):
                self.typecheck_for_loop(statement)
            elif isinstance(statement, FuncCall):
                self.typecheck_funccall(statement)
            elif isinstance(statement, ReturnStatement):
                self.typecheck_return_statement(statement)
            elif isinstance(statement, LoopControl):
                self.typecheck_loopcontrol(statement)
            else: assert False

    def typecheck_for_loop(self, for_loop):
        self.current_func.stack_size += 1
        self.typecheck_expr(for_loop.start)
        self.typecheck_expr(for_loop.stop)
        self.typecheck_expr(for_loop.step)
        self.typecheck_block(for_loop.block)

    def typecheck_while_loop(self, while_loop):
        self.typecheck_expr(while_loop.condition)
        self.typecheck_block(while_loop.block)

    def typecheck_loopcontrol(self, loopcontrol):
        pass

    def typecheck_if_statement(self, if_statement):
        self.typecheck_block(if_statement.block)
        self.typecheck_expr(if_statement.condition)
        if isinstance(if_statement.else_block, IfStatement):
            self.typecheck_if_statement(if_statement.else_block)
        elif isinstance(if_statement.else_block, Block):
            self.typecheck_block(if_statement.else_block)

    def typecheck_varassign(self, varassign):
        self.typecheck_expr(varassign.expr)
        if varassign.op.kind != TokenKind.EQUAL:
            binaryop = BinaryOp()
            binaryop.eval_kind = EvalKind.INT
            binaryop.lhs = Literal()
            binaryop.lhs.token = varassign.ident
            deref_depth = varassign.deref_depth
            while deref_depth > 0:
                unaryop = UnaryOp()
                unaryop.eval_kind = EvalKind.INT
                unaryop.op = Token(TokenKind.LESS_THAN, "", -1)
                unaryop.expr = binaryop.lhs

                binaryop.lhs = unaryop
                deref_depth -= 1

            binaryop.rhs = varassign.expr
            if varassign.op.kind == TokenKind.PLUS_EQUAL:
                binaryop.op = Token(TokenKind.PLUS, "", -1)
            elif varassign.op.kind == TokenKind.MINUS_EQUAL:
                binaryop.op = Token(TokenKind.MINUS, "", -1)
            elif varassign.op.kind == TokenKind.STAR_EQUAL:
                binaryop.op = Token(TokenKind.STAR, "", -1)
            elif varassign.op.kind == TokenKind.SLASH_EQUAL:
                binaryop.op = Token(TokenKind.SLASH, "", -1)
            else: assert False

            varassign.op.kind = TokenKind.EQUAL
            varassign.expr = binaryop

    def typecheck_vardecl(self, vardecl):
        if vardecl.kind.kind == TokenKind.IDENT:
            stack_size = self.structident_to_stacksize[vardecl.kind.value]
            vardecl.stack_size = stack_size

        self.current_func.stack_size += vardecl.stack_size
        if vardecl.expr != None:
            self.typecheck_expr(vardecl.expr)

    def typecheck_expr(self, expr):
        if isinstance(expr, Literal):
            self.typecheck_literal(expr)
        elif isinstance(expr, UnaryOp):
            self.typecheck_unaryop(expr)
        elif isinstance(expr, BinaryOp):
            self.typecheck_binaryop(expr)
        elif isinstance(expr, FuncCall):
            self.typecheck_funccall(expr)
        else: assert False, f"\n{expr}"

    def typecheck_literal(self, literal):
        if literal.token.kind == TokenKind.INT_LITERAL:
            literal.eval_kind = EvalKind.INT
        elif literal.token.kind == TokenKind.IDENT:
            pass
        else: assert False, f"\n{literal}"

    def typecheck_unaryop(self, unaryop):
        self.typecheck_expr(unaryop.expr)
        op_kind = unaryop.op.kind
        if op_kind == TokenKind.PLUS or \
           op_kind == TokenKind.MINUS:
            unaryop.eval_kind = EvalKind.INT
        elif op_kind == TokenKind.LESS_THAN:
            unaryop.eval_kind = EvalKind.INT
        elif op_kind == TokenKind.GREATER_THAN:
            unaryop.eval_kind = EvalKind.PTR
        else: assert False, f"\n{unaryop}"

    def typecheck_binaryop(self, binaryop):
        self.typecheck_expr(binaryop.lhs)
        self.typecheck_expr(binaryop.rhs)
        op_kind = binaryop.op.kind
        if op_kind == TokenKind.PLUS or \
           op_kind == TokenKind.MINUS or \
           op_kind == TokenKind.STAR:
            binaryop.eval_kind = EvalKind.INT
        elif op_kind == TokenKind.TWO_EQUAL or \
             op_kind == TokenKind.EXMARK_EQUAL or \
             op_kind == TokenKind.LESS_THAN or \
             op_kind == TokenKind.LESS_THAN_EQUAL or \
             op_kind == TokenKind.GREATER_THAN or \
             op_kind == TokenKind.GREATER_THAN_EQUAL or \
             op_kind == TokenKind.TWO_AMPERSAND or \
             op_kind == TokenKind.TWO_VERT_LINE:
            binaryop.eval_kind = EvalKind.BOOL
        else: assert False, f"\n{binaryop}"


class EvalKind(Enum):
    INT     = 0
    BOOL    = 1
    VOID    = 2
    PTR     = 3


    def __str__(self):
        return self.name
