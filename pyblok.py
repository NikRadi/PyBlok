from blok.codegen_bytecode import CodeGenByteCode
from blok.blok_vm import interp_bytecode
from blok.error import errors
from blok.lexer import Lexer
from blok.parsing import parse_blkprogram
from blok.typechecker import TypeChecker


def main():
    filename = "Main.blk"
    text = ""
    blkfile = open(filename)
    for line in blkfile:
        text += line

    blkfile.close()
    lexer = Lexer(text)
    ast = parse_blkprogram(lexer)
    TypeChecker(ast)
    print(ast)
    if len(errors) > 0:
        print("Could not compile")
        for err in errors:
            err.filename = filename
            print(err)

        return

    bytecode = CodeGenByteCode(ast).gen_bytecode()
    interp_bytecode(bytecode)


if __name__ == "__main__":
    main()
