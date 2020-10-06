from blok.codegen_bytecode import CodeGenByteCode
from blok.blok_vm import interp_bytecode
from blok.error import report_errors, errors
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
    if len(errors) > 0:
        report_errors()
        return

    bytecode = CodeGenByteCode(ast).gen_bytecode()
    interp_bytecode(bytecode)


if __name__ == "__main__":
    main()
