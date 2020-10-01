from copy import deepcopy
from enum import Enum
from blok.token import TokenKind
from blok.typechecker import EvalKind
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


class ByteCode(Enum):
    STOP                        =  0
    LABEL                       =  1
    PUSH_CONST                  =  2
    LOAD_VALUE_AT_IDX           =  3
    STORE_VALUE_AT_IDX          =  4
    INCR_STACK_BY_CONST         =  5
    LOAD_BASE_POINTER           =  6
    UNARYOP_NEG                 =  7
    BINARYOP_ADD                =  8
    BINARYOP_SUB                =  9
    BINARYOP_MUL                = 10
    BINARYOP_DIV                = 11
    JUMP                        = 12
    JUMP_IF_EQUAL               = 13
    JUMP_IF_NOT_EQUAL           = 14
    JUMP_IF_LESS_THAN           = 15
    JUMP_IF_LESS_THAN_EQUAL     = 16
    JUMP_IF_GREATER_THAN        = 17
    JUMP_IF_GREATER_THAN_EQUAL  = 18
    CALL_PROCEDURE              = 19
    RETURN                      = 20


    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class CodeGenByteCode:
    def __init__(self, ast):
        self.ast = ast
        self.localvar_idx = 0
        self.bytecode = []
        self.localvar_to_idx = {}
        self.funcident_to_label = {}
        self.label_to_idx = {}

    def replace_labels_by_idx(self):
        for i in range(len(self.bytecode)):
            code = self.bytecode[i]
            if code[0] == ByteCode.CALL_PROCEDURE:
                func_label = self.funcident_to_label[code[1]]
                self.bytecode[i] = (code[0], func_label, code[2])

        i = 0
        while True:
            if i == len(self.bytecode):
                break

            code = self.bytecode[i]
            if code[0] == ByteCode.LABEL:
                self.label_to_idx[code[1]] = i
                del self.bytecode[i]
            else:
                i += 1

        for i in range(len(self.bytecode)):
            code = self.bytecode[i]
            if len(code) == 2 and isinstance(code[1], str):
                self.bytecode[i] = (code[0], self.label_to_idx[code[1]])
            elif len(code) == 3 and isinstance(code[1], str):
                self.bytecode[i] = (code[0], self.label_to_idx[code[1]], code[2])

    def add_var(self, ident):
        idx = self.localvar_idx
        self.localvar_idx += 1
        self.localvar_to_idx[ident] = idx
        return idx

    def get_new_label(self):
        label_name = f"L{len(self.label_to_idx)}"
        self.label_to_idx[label_name] = 0
        return label_name

    def gen_bytecode(self):
        self.bytecode = [
            (ByteCode.CALL_PROCEDURE, "Main", 0),
            (ByteCode.STOP,)
        ]

        self.gen_bytecode_blkfile()
        for i, j in enumerate(self.bytecode): print(i, j)
        len_bfr = len(self.bytecode)
        self.optimize_bytecode()
        for i, j in enumerate(self.bytecode): print(i, j)
        print()
        len_aft = len(self.bytecode)
        print(f"Optimized {len_bfr - len_aft}")
        print()
        self.replace_labels_by_idx()
        return self.bytecode

    def optimize_bytecode(self):
        print("-" * 20)
        print("-" * 20)
        idx = 0
        while True:
            if idx >= len(self.bytecode):
                break

            code = self.bytecode[idx]
            if code[0] == ByteCode.BINARYOP_ADD:
                fst = self.bytecode[idx - 1]
                snd = self.bytecode[idx - 2]
                if fst[0] == ByteCode.PUSH_CONST and fst[1] == 0:
                    del self.bytecode[idx]
                    del self.bytecode[idx - 1]
                    idx -= 1
                    continue
                elif snd[0] == ByteCode.PUSH_CONST and snd[1] == 0:
                    del self.bytecode[idx]
                    del self.bytecode[idx - 2]
                    idx -= 1
                    continue
            elif code[0] == ByteCode.INCR_STACK_BY_CONST:
                if code[1] == 0:
                    del self.bytecode[idx]
                    continue
            else:
                print(code)

            idx += 1

        print("-" * 20)
        print("-" * 20)

    def gen_bytecode_blkfile(self):
        for funcdecl in self.ast.funcdecls:
            self.gen_bytecode_funcdecl(funcdecl)

    def gen_bytecode_return_statement(self, return_statement):
        num_returns = 0
        if return_statement.expr != None:
            num_returns = 1
            self.gen_bytecode_expr(return_statement.expr)

        self.bytecode += [(ByteCode.RETURN, num_returns)]

    def gen_bytecode_funccall(self, funccall):
        for arg in funccall.args:
            self.gen_bytecode_expr(arg)

        self.bytecode += [(ByteCode.CALL_PROCEDURE, funccall.ident.value, len(funccall.args))]

    def gen_bytecode_funcdecl(self, funcdecl):
        self.localvar_idx = 0
        self.localvar_to_idx = {}
        start_label = self.get_new_label()
        self.funcident_to_label[funcdecl.ident.value] = start_label
        self.bytecode += [
            (ByteCode.LABEL, start_label),
            (ByteCode.INCR_STACK_BY_CONST, funcdecl.stack_size)
        ]

        for param in funcdecl.params:
            self.add_var(param.ident.value)

        self.gen_bytecode_block(funcdecl.block)

    def gen_bytecode_block(self, block):
        vars_before = deepcopy(self.localvar_to_idx)
        for statement in block.statements:
            if isinstance(statement, VarDecl):
                self.gen_bytecode_vardecl(statement)
            elif isinstance(statement, VarAssign):
                self.gen_bytecode_varassign(statement)
            elif isinstance(statement, IfStatement):
                self.gen_bytecode_if_statement(statement)
            elif isinstance(statement, WhileLoop):
                self.gen_bytecode_while_loop(statement)
            elif isinstance(statement, ForLoop):
                self.gen_bytecode_for_loop(statement)
            elif isinstance(statement, FuncCall):
                self.gen_bytecode_funccall(statement)
            elif isinstance(statement, ReturnStatement):
                self.gen_bytecode_return_statement(statement)
            elif isinstance(statement, LoopControl):
                self.gen_bytecode_loopcontrol(statement)
            else: assert False

        self.localvar_to_idx = vars_before

    def gen_bytecode_for_loop(self, for_loop):
        idx = self.add_var(for_loop.var_ident.value)
        self.gen_bytecode_expr(for_loop.start)
        for_loop.start_label = self.get_new_label()
        self.bytecode += [
            (ByteCode.LOAD_BASE_POINTER,),
            (ByteCode.PUSH_CONST, idx),
            (ByteCode.BINARYOP_ADD,),
            (ByteCode.STORE_VALUE_AT_IDX,),
            (ByteCode.LABEL, for_loop.start_label)
        ]

        self.gen_bytecode_expr(for_loop.stop)
        for_loop.end_label = self.get_new_label()
        self.bytecode += [
            (ByteCode.LOAD_BASE_POINTER,),
            (ByteCode.PUSH_CONST, idx),
            (ByteCode.BINARYOP_ADD,),
            (ByteCode.LOAD_VALUE_AT_IDX,),
            (ByteCode.JUMP_IF_LESS_THAN, for_loop.end_label)
        ]

        for_loop.step_label = self.get_new_label()
        self.gen_bytecode_block(for_loop.block)
        self.bytecode += [(ByteCode.LABEL, for_loop.step_label)]
        self.gen_bytecode_expr(for_loop.step)
        self.bytecode += [
            (ByteCode.LOAD_BASE_POINTER,),
            (ByteCode.PUSH_CONST, idx),
            (ByteCode.BINARYOP_ADD,),
            (ByteCode.LOAD_VALUE_AT_IDX,),
            (ByteCode.BINARYOP_ADD,),

            (ByteCode.LOAD_BASE_POINTER,),
            (ByteCode.PUSH_CONST, idx),
            (ByteCode.BINARYOP_ADD,),
            (ByteCode.STORE_VALUE_AT_IDX,),

            (ByteCode.JUMP, for_loop.start_label),
            (ByteCode.LABEL, for_loop.end_label)
        ]

    def gen_bytecode_while_loop(self, while_loop):
        while_loop.start_label = self.get_new_label()
        while_loop.end_label = self.get_new_label()
        self.bytecode += [(ByteCode.LABEL, while_loop.start_label)]
        self.gen_bytecode_expr(while_loop.condition)
        self.bytecode[-1] = (self.bytecode[-1][0], while_loop.end_label)
        self.gen_bytecode_block(while_loop.block)
        self.bytecode += [(ByteCode.JUMP, while_loop.start_label)]
        self.bytecode += [(ByteCode.LABEL, while_loop.end_label)]

    def gen_bytecode_loopcontrol(self, loopcontrol):
        if loopcontrol.kind == LoopControlKind.BREAK:
            self.bytecode += [(ByteCode.JUMP, loopcontrol.parent_loop.end_label)]
        elif loopcontrol.kind == LoopControlKind.CONTINUE:
            self.bytecode += [(ByteCode.JUMP, loopcontrol.parent_loop.step_label)]

    def gen_bytecode_if_statement(self, if_statement):
        self.gen_bytecode_expr(if_statement.condition)
        else_label = self.get_new_label()
        self.bytecode[-1] = (self.bytecode[-1][0], else_label)
        self.gen_bytecode_block(if_statement.block)
        is_else_block_none = if_statement.else_block == None
        if not is_else_block_none:
            end_label = self.get_new_label()
            self.bytecode += [(ByteCode.JUMP, end_label)]

        self.bytecode += [(ByteCode.LABEL, else_label)]
        if isinstance(if_statement.else_block, IfStatement):
            self.gen_bytecode_if_statement(if_statement.else_block)
        elif isinstance(if_statement.else_block, Block):
            self.gen_bytecode_block(if_statement.else_block)

        if not is_else_block_none:
            self.bytecode += [(ByteCode.LABEL, end_label)]

    def gen_bytecode_varassign(self, varassign):
        self.gen_bytecode_expr(varassign.expr)
        idx = self.localvar_to_idx[varassign.ident.value]
        self.bytecode += [
            (ByteCode.LOAD_BASE_POINTER,),
            (ByteCode.PUSH_CONST, idx),
            (ByteCode.BINARYOP_ADD,),
        ]

        if varassign.arr_idx != None:
            self.bytecode += [
                (ByteCode.LOAD_VALUE_AT_IDX,),
                (ByteCode.PUSH_CONST, varassign.arr_idx),
                (ByteCode.BINARYOP_ADD,),
            ]
        elif varassign.deref_depth > 0:
            deref_depth = varassign.deref_depth
            while deref_depth > 0:
                self.bytecode += [(ByteCode.LOAD_VALUE_AT_IDX,)]
                deref_depth -= 1

        self.bytecode += [(ByteCode.STORE_VALUE_AT_IDX,)]

    def gen_bytecode_vardecl(self, vardecl):
        is_array = vardecl.stack_size > 1
        if is_array:
            self.localvar_idx += vardecl.stack_size - 1

        idx = self.add_var(vardecl.ident.value)
        if is_array:
            # TODO: If vardecl is a struct containing an array
            #       then first_elem_idx will point to where
            #       the variable-struct begins and not where
            #       the array in the struct begins
            first_elem_idx = idx - (vardecl.stack_size - 1)
            self.bytecode += [
                (ByteCode.LOAD_BASE_POINTER,),
                (ByteCode.PUSH_CONST, first_elem_idx),
                (ByteCode.BINARYOP_ADD,),

                (ByteCode.LOAD_BASE_POINTER,),
                (ByteCode.PUSH_CONST, idx),
                (ByteCode.BINARYOP_ADD,),
                (ByteCode.STORE_VALUE_AT_IDX,)
            ]
        elif vardecl.expr != None:
            self.gen_bytecode_expr(vardecl.expr)
            self.bytecode += [
                (ByteCode.LOAD_BASE_POINTER,),
                (ByteCode.PUSH_CONST, idx),
                (ByteCode.BINARYOP_ADD,),
                (ByteCode.STORE_VALUE_AT_IDX,)
            ]


    def gen_bytecode_expr(self, expr):
        if isinstance(expr, Literal):
            self.gen_bytecode_literal(expr)
        elif isinstance(expr, FuncCall):
            self.gen_bytecode_funccall(expr)
        elif expr.eval_kind == EvalKind.INT:
            self.gen_bytecode_arith_expr(expr)
        elif expr.eval_kind == EvalKind.BOOL:
            self.gen_bytecode_logic_expr(expr)
        elif expr.eval_kind == EvalKind.PTR:
            self.gen_bytecode_ptr_expr(expr)
        else: assert False, f"\n{expr}"

    def gen_bytecode_arith_expr(self, expr):
        if isinstance(expr, UnaryOp):
            self.gen_bytecode_arith_unaryop(expr)
        elif isinstance(expr, BinaryOp):
            self.gen_bytecode_arith_binaryop(expr)
        else: assert False, f"\n{expr}"

    def gen_bytecode_logic_expr(self, expr):
        if isinstance(expr, BinaryOp):
            self.gen_bytecode_logic_binaryop(expr)
        else: assert False

    def gen_bytecode_ptr_expr(self, expr):
        if isinstance(expr, UnaryOp):
            self.gen_bytecode_ptr_unaryop(expr)
        else: assert False

    def gen_bytecode_literal(self, literal):
        if literal.token.kind == TokenKind.IDENT:
            idx = self.localvar_to_idx[literal.token.value]
            self.bytecode += [
                (ByteCode.LOAD_BASE_POINTER,),
                (ByteCode.PUSH_CONST, idx),
                (ByteCode.BINARYOP_ADD,),
                (ByteCode.LOAD_VALUE_AT_IDX,)
            ]

            if literal.arr_idx != None:
                self.bytecode += [
                    (ByteCode.PUSH_CONST, literal.arr_idx),
                    (ByteCode.BINARYOP_ADD,),
                    (ByteCode.LOAD_VALUE_AT_IDX,),
                ]
        elif literal.token.kind == TokenKind.INT_LITERAL:
            self.bytecode += [(ByteCode.PUSH_CONST, literal.token.value)]
        else: assert False

    def gen_bytecode_arith_unaryop(self, unaryop):
        self.gen_bytecode_expr(unaryop.expr)
        if unaryop.op.kind == TokenKind.MINUS:
            self.bytecode += [(ByteCode.UNARYOP_NEG,)]
        elif unaryop.op.kind == TokenKind.LESS_THAN:
            self.bytecode += [
                (ByteCode.LOAD_VALUE_AT_IDX,)
            ]
        else: assert False, f"\n{unaryop}"

    def gen_bytecode_arith_binaryop(self, binaryop):
        self.gen_bytecode_expr(binaryop.lhs)
        self.gen_bytecode_expr(binaryop.rhs)
        op_kind = binaryop.op.kind
        if   op_kind == TokenKind.PLUS:  self.bytecode += [(ByteCode.BINARYOP_ADD,)]
        elif op_kind == TokenKind.MINUS: self.bytecode += [(ByteCode.BINARYOP_SUB,)]
        elif op_kind == TokenKind.STAR:  self.bytecode += [(ByteCode.BINARYOP_MUL,)]
        elif op_kind == TokenKind.SLASH: self.bytecode += [(ByteCode.BINARYOP_DIV,)]
        else: assert False

    def gen_bytecode_logic_binaryop(self, binaryop):
        self.gen_bytecode_expr(binaryop.lhs)
        self.gen_bytecode_expr(binaryop.rhs)
        jump_kind = None
        if binaryop.op.kind == TokenKind.TWO_EQUAL:
            jump_kind = ByteCode.JUMP_IF_NOT_EQUAL
        elif binaryop.op.kind == TokenKind.EXMARK_EQUAL:
            jump_kind = ByteCode.JUMP_IF_EQUAL
        elif binaryop.op.kind == TokenKind.LESS_THAN:
            jump_kind = ByteCode.JUMP_IF_GREATER_THAN_EQUAL
        elif binaryop.op.kind == TokenKind.LESS_THAN_EQUAL:
            jump_kind = ByteCode.JUMP_IF_GREATER_THAN
        elif binaryop.op.kind == TokenKind.GREATER_THAN:
            jump_kind = ByteCode.JUMP_IF_LESS_THAN_EQUAL
        elif binaryop.op.kind == TokenKind.GREATER_THAN_EQUAL:
            jump_kind = ByteCode.JUMP_IF_LESS_THAN
        else:
            assert False, f"{binaryop}"

        # NOTE: Label is not added here but by parent
        self.bytecode += [(jump_kind,)]

    def gen_bytecode_ptr_unaryop(self, unaryop):
        varidx = self.localvar_to_idx[unaryop.expr.token.value]
        self.bytecode += [
            (ByteCode.LOAD_BASE_POINTER,),
            (ByteCode.PUSH_CONST, varidx),
            (ByteCode.BINARYOP_ADD,)
        ]
