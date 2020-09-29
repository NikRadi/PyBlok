import blok.astnodes
from blok.token import Token, TokenKind
from blok.astnodes import (
    BlkProgram,
    ReturnStatement,
    FuncCall,
    FuncDecl,
    Block,
    ForLoop,
    WhileLoop,
    BreakStatement,
    IfStatement,
    VarAssign,
    VarDecl,
    Literal,
    UnaryOp,
    BinaryOp
)


def get_precedence(op_kind):
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
    return -1


def parse_blkprogram(lexer):
    blkprogram = BlkProgram()
    while lexer.peek_token().kind != TokenKind.EOF:
        blkprogram.funcdecls.append(parse_funcdecl(lexer))

    return blkprogram


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
    lexer.eat_next_token() # (
    while lexer.peek_token().kind != TokenKind.ROUND_BRAC_RIGHT:
        if lexer.peek_token().kind == TokenKind.COMMA and len(funcdecl.params) > 0:
            lexer.eat_next_token()

        vardecl = VarDecl()
        vardecl.kind = lexer.peek_token()
        lexer.eat_next_token()
        vardecl.ident = lexer.peek_token()
        lexer.eat_next_token()
        funcdecl.params.append(vardecl)

    lexer.eat_next_token() # )
    funcdecl.block = parse_block(lexer, funcdecl)
    return funcdecl


def parse_block(lexer, parent):
    block = Block()
    block.parent = parent
    assert lexer.peek_token().kind == TokenKind.CURLY_BRAC_LEFT, lexer.peek_token().kind
    lexer.eat_next_token() # {
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
                 peek1.kind == TokenKind.SLASH_EQUAL:
                block.statements.append(parse_varassign(lexer))
            else: assert False, f"\n{peek}"
        elif peek.kind == TokenKind.LESS_THAN:
            block.statements.append(parse_varassign(lexer))
        elif peek.kind == TokenKind.INT or \
             peek.kind == TokenKind.INT_PTR:
            block.statements.append(parse_vardecl(lexer))
        elif peek.kind == TokenKind.IF:
            block.statements.append(parse_if_statement(lexer, block))
        elif peek.kind == TokenKind.WHILE:
            block.statements.append(parse_while_loop(lexer))
        elif peek.kind == TokenKind.FOR:
            block.statements.append(parse_for_loop(lexer))
        elif peek.kind == TokenKind.RETURN:
            block.statements.append(parse_return_statement(lexer))
        elif peek.kind == TokenKind.BREAK:
            block.statements.append(parse_break_statement(lexer, block))
        else: assert False, f"\n{lexer.peek_token()}"

    lexer.eat_next_token() # }
    return block


def parse_for_loop(lexer):
    for_loop = ForLoop()
    lexer.eat_next_token() # for
    for_loop.var_ident = lexer.peek_token()
    lexer.eat_next_token()
    lexer.eat_next_token() # =
    for_loop.start = parse_expr(lexer)
    lexer.eat_next_token() # ..
    for_loop.stop = parse_expr(lexer)
    lexer.eat_next_token() # step
    for_loop.step = parse_expr(lexer)
    for_loop.block = parse_block(lexer, for_loop)
    return for_loop


def parse_while_loop(lexer):
    while_loop = WhileLoop()
    lexer.eat_next_token() # while
    while_loop.condition = parse_expr(lexer)
    while_loop.block = parse_block(lexer, while_loop)
    return while_loop


def parse_break_statement(lexer, parent):
    break_statement = BreakStatement()
    break_statement.parent = parent
    lexer.eat_next_token() # break
    lexer.eat_next_token() # ;
    break_statement.parent_loop = parent
    while True:
        if isinstance(break_statement.parent_loop, ForLoop) or \
           isinstance(break_statement.parent_loop, WhileLoop):
            break

        break_statement.parent_loop = break_statement.parent_loop.parent

    return break_statement


def parse_if_statement(lexer, parent):
    if_statement = IfStatement()
    if_statement.parent = parent
    lexer.eat_next_token() # if
    if_statement.condition = parse_expr(lexer)
    if_statement.block = parse_block(lexer, if_statement)
    if lexer.peek_token().kind == TokenKind.ELSE:
        lexer.eat_next_token()
        if lexer.peek_token().kind == TokenKind.CURLY_BRAC_LEFT:
            # TODO: if_statement.block and if_statement.else_block are not the same block
            #       but the block will be assigned the same parent
            if_statement.else_block = parse_block(lexer, if_statement)
        elif lexer.peek_token().kind == TokenKind.IF:
            if_statement.else_block = parse_if_statement(lexer, if_statement)
        else: assert False

    return if_statement


def parse_varassign(lexer):
    varassign = VarAssign()
    if lexer.peek_token().kind == TokenKind.LESS_THAN:
        varassign.deref = True
        lexer.eat_next_token()

    varassign.ident = lexer.peek_token()
    lexer.eat_next_token()
    varassign.op = lexer.peek_token()
    lexer.eat_next_token()
    varassign.expr = parse_expr(lexer)
    lexer.eat_next_token() # ;
    return varassign


def parse_vardecl(lexer):
    vardecl = VarDecl()
    vardecl.kind = lexer.peek_token()
    lexer.eat_next_token()
    vardecl.ident = lexer.peek_token()
    lexer.eat_next_token()
    if lexer.peek_token().kind == TokenKind.SEMICOLON:
        lexer.eat_next_token() # ;
        return vardecl

    lexer.eat_next_token() # =
    vardecl.expr = parse_expr(lexer)
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
       token.kind == TokenKind.LESS_THAN or \
       token.kind == TokenKind.GREATER_THAN:
        lexer.eat_next_token()
        unaryop = UnaryOp()
        unaryop.op = token
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
        return literal

    if token.kind == TokenKind.IDENT:
        literal = Literal()
        literal.token = token
        lexer.eat_next_token()
        return literal

    assert False, f"\n{token}"
