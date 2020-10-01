from blok.codegen_bytecode import ByteCode


def optimize_bytecode(bytecode):
    print("-" * 20)
    idx = 0
    while True:
        if idx >= len(bytecode):
            break

        code = bytecode[idx]
        if code[0] == ByteCode.BINARYOP_ADD:
            fst = bytecode[idx - 1]
            snd = bytecode[idx - 2]
            if fst[0] == ByteCode.PUSH_CONST and fst[1] == 0:
                del bytecode[idx]
                del bytecode[idx - 1]
                idx -= 1
                continue
            elif snd[0] == ByteCode.PUSH_CONST and snd[1] == 0:
                del bytecode[idx]
                del bytecode[idx - 2]
                idx -= 1
                continue
        elif code[0] == ByteCode.INCR_STACK_BY_CONST:
            if code[1] == 0:
                del bytecode[idx]
                continue
        else:
            print(code)

        idx += 1

    print("-" * 20)
    return bytecode
