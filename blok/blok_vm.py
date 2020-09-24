from blok.codegen_bytecode import ByteCode


def interp_bytecode(bytecode):
    pc = 0 # program counter
    sp = 0 # stack pointer
    bp = 0 # base pointer
    stack = [0] * 100
    while True:
        code = bytecode[pc]
        if code[0] == ByteCode.STOP:
            break
        elif code[0] == ByteCode.PUSH_CONST:
            stack[sp] = code[1]
            sp += 1
        elif code[0] == ByteCode.LOAD_VALUE_AT_IDX:
            idx = stack[sp - 1]
            stack[sp - 1] = stack[idx]
        elif code[0] == ByteCode.STORE_VALUE_AT_IDX:
            sp -= 2
            idx = stack[sp + 1]
            value = stack[sp]
            stack[idx] = value
        elif code[0] == ByteCode.LOAD_BASE_POINTER:
            stack[sp] = bp
            sp += 1
        elif code[0] == ByteCode.UNARYOP_NEG:
            idx = sp - 1
            stack[idx] = -stack[idx]
        elif code[0] == ByteCode.BINARYOP_ADD:
            sp -= 1
            stack[sp - 1] += stack[sp]
        elif code[0] == ByteCode.BINARYOP_SUB:
            sp -= 1
            stack[sp - 1] -= stack[sp]
        elif code[0] == ByteCode.BINARYOP_MUL:
            sp -= 1
            stack[sp - 1] *= stack[sp]
        elif code[0] == ByteCode.INCR_STACK_BY_CONST:
            sp += code[1]
        elif code[0] == ByteCode.JUMP:
            pc = code[1] - 1
        elif code[0] == ByteCode.JUMP_IF_EQUAL:
            sp -= 2
            if stack[sp] == stack[sp + 1]: pc = code[1] - 1
        elif code[0] == ByteCode.JUMP_IF_NOT_EQUAL:
            sp -= 2
            if stack[sp] != stack[sp + 1]: pc = code[1] - 1
        elif code[0] == ByteCode.JUMP_IF_LESS_THAN:
            sp -= 2
            if stack[sp] < stack[sp + 1]: pc = code[1] - 1
        elif code[0] == ByteCode.JUMP_IF_LESS_THAN_EQUAL:
            sp -= 2
            if stack[sp] <= stack[sp + 1]: pc = code[1] - 1
        elif code[0] == ByteCode.JUMP_IF_GREATER_THAN:
            sp -= 2
            if stack[sp] > stack[sp + 1]: pc = code[1] - 1
        elif code[0] == ByteCode.JUMP_IF_GREATER_THAN_EQUAL:
            sp -= 2
            if stack[sp] >= stack[sp + 1]: pc = code[1] - 1
        elif code[0] == ByteCode.CALL_PROCEDURE:
            sp -= code[2]
            for i in range(code[2]):
                stack[sp + i + 2] = stack[sp + i]

            stack[sp] = pc
            stack[sp + 1] = bp
            sp += 2
            bp = sp
            pc = code[1] - 1
        elif code[0] == ByteCode.RETURN:
            bp -= 2
            new_pc = stack[bp]
            new_bp = stack[bp + 1]
            stack[bp] = stack[sp - 1]
            sp = bp + code[1]
            pc = new_pc
            bp = new_bp
        else:
            assert False, code

        pc += 1
        print(f"{bp},{sp},{code[0]:<30}{code[1] if len(code) > 1 else '':<5}{stack[:sp]}")
