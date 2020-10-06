import sys
import blok.astnodes
from blok.error import add_err_exit, report_exit
from blok.token import Token, TokenKind
from blok.astnodes import (
    BlkProgram,
    Struct,
    ReturnStatement,
    FuncCall,
    FuncDecl,
    Block,
    ForLoop,
    WhileLoop,
    LoopControl,
    LoopControlKind,
    IfStatement,
    VarDecl,
    Literal,
    UnaryOp,
    BinaryOp
)


def get_precedence(op_kind):
    if op_kind == TokenKind.DOT:                return 60
    if op_kind == TokenKind.STAR or \
       op_kind == TokenKind.SLASH:              return 50
    if op_kind == TokenKind.PLUS or \
       op_kind == TokenKind.MINUS:              return 40
    if op_kind == TokenKind.LESS_THAN or \
       op_kind == TokenKind.LESS_THAN_EQUAL or \
       op_kind == TokenKind.GREATER_THAN or \
       op_kind == TokenKind.GREATER_THAN_EQUAL: return 30
    if op_kind == TokenKind.TWO_EQUAL or \
       op_kind == TokenKind.EXMARK_EQUAL:       return 20
    if op_kind == TokenKind.TWO_AMPERSAND or \
       op_kind == TokenKind.TWO_VERT_LINE:      return 10
    return -1


def expect(lexer, kind):
    token = lexer.peek_token()
    if not token.kind == kind:
        if token.kind == TokenKind.INVALID:
            report_exit()
        else:
            add_err_exit(token.line, f"expected '{kind}' but got '{token.kind}'")

    lexer.eat_next_token()
    return token


def parse_blkprogram(lexer):
    blkprogram = BlkProgram()
    peek = lexer.peek_token()
    while peek.kind != TokenKind.EOF:
        if peek.kind == TokenKind.STRUCT:
            blkprogram.structs.append(parse_struct(lexer))
        elif peek.kind == TokenKind.VOID or peek == TokenKind.INT:
            blkprogram.funcdecls.append(parse_funcdecl(lexer))
        elif peek.kind == TokenKind.INVALID:
            report_exit()
        else:
            add_err_exit(peek.line, f"invalid statement in global scope '{peek.value}'")

        peek = lexer.peek_token()

    return blkprogram


def parse_struct(lexer):
    struct = Struct()
    lexer.eat_next_token()
    struct.ident = lexer.peek_token()
    lexer.eat_next_token()
    lexer.eat_next_token() # {
    while lexer.peek_token().kind != TokenKind.CURLY_BRAC_RIGHT:
        struct.vardecls.append(parse_vardecl(lexer))

    for vardecl in struct.vardecls:
        struct.stack_size += vardecl.stack_size

    lexer.eat_next_token() # }
    return struct


def parse_return_statement(lexer):
    return_statement = ReturnStatement()
    lexer.eat_next_token()
    if lexer.peek_token().kind != TokenKind.SEMICOLON:
        return_statement.expr = parse_expr(lexer)

    lexer.eat_next_token() # ;
    return return_statement


def parse_funccall(lexer):
    funccall = FuncCall()
    funccall.ident = lexer.peek_token()
    lexer.eat_next_token()
    lexer.eat_next_token() # (
    while lexer.peek_token().kind != TokenKind.ROUND_BRAC_RIGHT:
        if lexer.peek_token().kind == TokenKind.COMMA and len(funccall.args) > 0:
            lexer.eat_next_token()

        funccall.args.append(parse_expr(lexer))

    lexer.eat_next_token() # )
    return funccall


def parse_funcdecl(lexer):
    funcdecl = FuncDecl()
    funcdecl.return_token = lexer.peek_token()
    lexer.eat_next_token()
    funcdecl.ident = lexer.peek_token()
    lexer.eat_next_token()
    expect(lexer, TokenKind.ROUND_BRAC_LEFT)
    while lexer.peek_token().kind != TokenKind.ROUND_BRAC_RIGHT:
        if lexer.peek_token().kind == TokenKind.COMMA and len(funcdecl.params) > 0:
            lexer.eat_next_token()

        funcdecl.params.append(parse_vardecl(lexer, False, False))

    expect(lexer, TokenKind.ROUND_BRAC_RIGHT)
    funcdecl.block = parse_block(lexer, funcdecl)
    return funcdecl


def parse_block(lexer, parent):
    block = Block()
    block.parent = parent
    expect(lexer, TokenKind.CURLY_BRAC_LEFT)
    while lexer.peek_token().kind != TokenKind.CURLY_BRAC_RIGHT:
        peek = lexer.peek_token()
        if peek.kind == TokenKind.IDENT:
            peek1 = lexer.peek_token(1)
            if peek1.kind == TokenKind.ROUND_BRAC_LEFT:
                block.statements.append(parse_funccall(lexer))
                lexer.eat_next_token() # ;
            elif peek1.kind == TokenKind.EQUAL or \
                 peek1.kind == TokenKind.PLUS_EQUAL or \
                 peek1.kind == TokenKind.MINUS_EQUAL or \
                 peek1.kind == TokenKind.STAR_EQUAL or \
                 peek1.kind == TokenKind.SLASH_EQUAL or \
                 peek1.kind == TokenKind.SQUARE_BRAC_LEFT or \
                 peek1.kind == TokenKind.DOT:
                block.statements.append(parse_varassign(lexer))
            else: # It is a struct-variable
                block.statements.append(parse_vardecl(lexer))
        elif peek.kind == TokenKind.LESS_THAN:
            block.statements.append(parse_varassign(lexer))
        elif peek.kind == TokenKind.INT:
            block.statements.append(parse_vardecl(lexer))
        elif peek.kind == TokenKind.IF:
            block.statements.append(parse_if_statement(lexer, block))
        elif peek.kind == TokenKind.WHILE:
            block.statements.append(parse_while_loop(lexer))
        elif peek.kind == TokenKind.FOR:
            block.statements.append(parse_for_loop(lexer))
        elif peek.kind == TokenKind.RETURN:
            block.statements.append(parse_return_statement(lexer))
        elif peek.kind == TokenKind.BREAK or \
             peek.kind == TokenKind.CONTINUE:
            block.statements.append(parse_loopcontrol(lexer, block))
        else: add_err_exit(peek.line, f"invalid statement starting with '{peek.kind}'")

    expect(lexer, TokenKind.CURLY_BRAC_RIGHT)
    return block


def parse_for_loop(lexer):
    for_loop = ForLoop()
    expect(lexer, TokenKind.FOR)
    for_loop.var_ident = lexer.peek_token()
    lexer.eat_next_token()
    expect(lexer, TokenKind.EQUAL)
    for_loop.start = parse_expr(lexer)
    expect(lexer, TokenKind.TWO_DOT)
    for_loop.stop = parse_expr(lexer)
    expect(lexer, TokenKind.STEP)
    for_loop.step = parse_expr(lexer)
    for_loop.block = parse_block(lexer, for_loop)
    return for_loop


def parse_while_loop(lexer):
    while_loop = WhileLoop()
    expect(lexer, TokenKind.WHILE)
    while_loop.condition = parse_expr(lexer)
    while_loop.block = parse_block(lexer, while_loop)
    return while_loop


def parse_loopcontrol(lexer, parent):
    loopcontrol = LoopControl()
    loopcontrol.parent = parent
    if lexer.peek_token().kind == TokenKind.BREAK:
        loopcontrol.kind = LoopControlKind.BREAK
    else:
        loopcontrol.kind = LoopControlKind.CONTINUE

    lexer.eat_next_token()
    expect(lexer, TokenKind.SEMICOLON)
    loopcontrol.parent_loop = parent
    while True:
        if isinstance(loopcontrol.parent_loop, ForLoop) or \
           isinstance(loopcontrol.parent_loop, WhileLoop):
            break

        loopcontrol.parent_loop = loopcontrol.parent_loop.parent

    return loopcontrol


def parse_if_statement(lexer, parent):
    if_statement = IfStatement()
    if_statement.parent = parent
    expect(lexer, TokenKind.IF)
    if_statement.condition = parse_expr(lexer)
    if_statement.block = parse_block(lexer, if_statement)
    if lexer.peek_token().kind == TokenKind.ELSE:
        lexer.eat_next_token()
        if lexer.peek_token().kind == TokenKind.CURLY_BRAC_LEFT:
            # TODO: if_statement.block and if_statement.else_block are not the same block
            #       but the block will be assigned the same parent
            #       this might cause a problem with loopcontrol
            if_statement.else_block = parse_block(lexer, if_statement)
        elif lexer.peek_token().kind == TokenKind.IF:
            if_statement.else_block = parse_if_statement(lexer, if_statement)
        else: assert False

    return if_statement


def parse_varassign(lexer):
    varassign = BinaryOp()
    varassign.lhs = parse_expr(lexer)
    varassign.op = lexer.peek_token()
    lexer.eat_next_token()
    varassign.rhs = parse_expr(lexer)
    expect(lexer, TokenKind.SEMICOLON)
    return varassign


def parse_vardecl(lexer, has_expr=True, eat_semicolon=True):
    vardecl = VarDecl()
    vardecl.kind = lexer.peek_token()
    lexer.eat_next_token()
    if lexer.peek_token().kind == TokenKind.GREATER_THAN:
        while lexer.peek_token().kind == TokenKind.GREATER_THAN:
            vardecl.ptr_depth += 1
            lexer.eat_next_token()
    elif lexer.peek_token().kind == TokenKind.SQUARE_BRAC_LEFT:
        lexer.eat_next_token() # [
        vardecl.stack_size = int(lexer.peek_token().value) + 1
        lexer.eat_next_token()
        lexer.eat_next_token() # ]

    vardecl.ident = expect(lexer, TokenKind.IDENT)
    if lexer.peek_token().kind == TokenKind.SEMICOLON or not has_expr:
        if eat_semicolon:
            lexer.eat_next_token() # ;

        return vardecl

    expect(lexer, TokenKind.EQUAL)
    vardecl.expr = parse_expr(lexer)
    if eat_semicolon:
        lexer.eat_next_token() # ;

    return vardecl


def parse_expr(lexer, min_precedence=0):
    lhs = parse_literal(lexer)
    while True:
        token_kind = lexer.peek_token().kind
        precedence = get_precedence(token_kind)
        if precedence < min_precedence:
            break

        binaryop = BinaryOp()
        binaryop.op = lexer.peek_token()
        lexer.eat_next_token()
        binaryop.rhs = parse_expr(lexer, precedence)
        binaryop.lhs = lhs
        lhs = binaryop

    return lhs


def parse_literal(lexer):
    token = lexer.peek_token()
    if token.kind == TokenKind.PLUS or \
       token.kind == TokenKind.MINUS or \
       token.kind == TokenKind.LESS_THAN:
        lexer.eat_next_token()
        unaryop = UnaryOp()
        unaryop.op = token
        unaryop.expr = parse_literal(lexer)
        return unaryop

    if token.kind == TokenKind.GREATER_THAN:
        lexer.eat_next_token()
        unaryop = UnaryOp()
        unaryop.op = token
        if lexer.peek_token(1).kind == TokenKind.DOT:
            unaryop.expr = parse_expr(lexer)
        else:
            unaryop.expr = parse_literal(lexer)

        return unaryop

    if token.kind == TokenKind.ROUND_BRAC_LEFT:
        lexer.eat_next_token() # (
        expr = parse_expr(lexer)
        lexer.eat_next_token() # )
        return expr

    if lexer.peek_token(1).kind == TokenKind.ROUND_BRAC_LEFT:
        return parse_funccall(lexer)

    if token.kind == TokenKind.INT_LITERAL:
        literal = Literal()
        literal.token = token
        lexer.eat_next_token()
        if lexer.peek_token().kind == TokenKind.SQUARE_BRAC_LEFT:
            lexer.eat_next_token() # [
            literal.offset = int(lexer.peek_token().value)
            lexer.eat_next_token()
            lexer.eat_next_token() # ]

        return literal

    if token.kind == TokenKind.IDENT:
        literal = Literal()
        literal.token = token
        lexer.eat_next_token()
        if lexer.peek_token().kind == TokenKind.SQUARE_BRAC_LEFT:
            lexer.eat_next_token() # [
            literal.offset = int(lexer.peek_token().value)
            lexer.eat_next_token()
            lexer.eat_next_token() # ]

        return literal

    add_err_exit(token.line, f"unexpected literal '{token.kind}'")
