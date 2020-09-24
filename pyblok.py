from codegen_bytecode import CodeGenByteCode
from blok_vm import interp_bytecode
from lexer import Lexer
from parsing import parse_blkprogram
from typechecker import TypeChecker


if __name__ == "__main__":
    text = ""
    blkfile = open("Main.blk")
    for line in blkfile:
        text += line

    blkfile.close()
    lexer = Lexer(text)
    ast = parse_blkprogram(lexer)
    TypeChecker(ast)
    bytecode = CodeGenByteCode(ast).gen_bytecode()
    interp_bytecode(bytecode)
