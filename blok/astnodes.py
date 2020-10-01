from enum import Enum


class AstNode:
    def __init__(self):
        self.parent = None

    def attributes_tostr(self):
        return ""

    def content_tostr(self, indent):
        return ""

    def tostr(self, indent=0):
        name = self.__class__.__name__
        result = f"{' ' * indent}<{name}"
        result += f"{self.attributes_tostr()}>\n"
        result += self.content_tostr(indent + 4)
        result += f"{' ' * indent}</{name}>\n"
        return result

    def __str__(self):
        return self.tostr()


class Expr(AstNode):
    def __init__(self):
        super().__init__()
        self.eval_kind = None

    def attributes_tostr(self):
        if self.eval_kind != None:
            return f" eval_kind=\"{self.eval_kind}\""
        return ""


class Loop(AstNode):
    def __init__(self):
        super().__init__()
        self.start_label = None
        self.end_label = None


class BlkProgram(AstNode):
    def __init__(self):
        super().__init__()
        self.structs = []
        self.funcdecls = []

    def content_tostr(self, indent):
        result = ""
        for struct in self.structs:
            result += struct.tostr(indent)

        for funcdecl in self.funcdecls:
            result += funcdecl.tostr(indent)

        return result


class Struct(AstNode):
    def __init__(self):
        super().__init__()
        self.stack_size = 0
        self.ident = None
        self.vardecls = []

    def attributes_tostr(self):
        return f" stack_size=\"{self.stack_size}\""

    def content_tostr(self, indent):
        result = f"{' ' * indent}{self.ident}\n"
        for vardecl in self.vardecls:
            result += vardecl.tostr(indent)

        return result


class ReturnStatement(AstNode):
    def __init__(self):
        super().__init__()
        self.expr = None


    def content_tostr(self, indent):
        if self.expr != None:
            return self.expr.tostr(indent)
        return ""


class FuncCall(AstNode):
    def __init__(self):
        self.eval_kind = None
        self.ident = None
        self.args = []

    def attributes_tostr(self):
        return f" eval_kind=\"{self.eval_kind}\""

    def content_tostr(self, indent):
        result = f"{' ' * indent}{self.ident}\n"
        for arg in self.args:
            result += arg.tostr(indent)

        return result


class FuncDecl(AstNode):
    def __init__(self):
        super().__init__()
        self.stack_size = None
        self.return_token = None
        self.params = []
        self.ident = None
        self.block = None

    def attributes_tostr(self):
        if self.stack_size != None:
            return f" stack_size=\"{self.stack_size}\""
        return ""

    def content_tostr(self, indent):
        result = f"{' ' * indent}{self.return_token}\n"
        result += f"{' ' * indent}{self.ident}\n"
        for param in self.params:
            result += param.tostr(indent)

        result += self.block.tostr(indent)
        return result


class Block(AstNode):
    def __init__(self):
        super().__init__()
        self.statements = []

    def content_tostr(self, indent):
        result = ""
        for statement in self.statements:
            result += statement.tostr(indent)

        return result


class ForLoop(Loop):
    def __init__(self):
        super().__init__()
        self.var_ident = None
        self.start = None
        self.stop = None
        self.step = None
        self.block = None
        self.step_label = None

    def content_tostr(self, indent):
        result = f"{' ' * (indent)}{self.var_ident}\n"
        result += self.start.tostr(indent)
        result += self.stop.tostr(indent)
        result += self.step.tostr(indent)
        result += self.block.tostr(indent)
        return result


class WhileLoop(Loop):
    def __init__(self):
        super().__init__()
        self.condition = None
        self.block = None

    def content_tostr(self, indent):
        result = self.condition.tostr(indent)
        result += self.block.tostr(indent)
        return result


class LoopControl(AstNode):
    def __init__(self):
        super().__init__()
        self.parent_loop = None
        self.kind = None


class LoopControlKind(Enum):
    BREAK    = 0
    CONTINUE = 1


class IfStatement(AstNode):
    def __init__(self):
        super().__init__()
        self.condition = None
        self.block = None
        self.else_block = None

    def content_tostr(self, indent):
        result = self.condition.tostr(indent)
        result += self.block.tostr(indent)
        if self.else_block != None:
            result += self.else_block.tostr(indent)

        return result


class VarDecl(AstNode):
    def __init__(self):
        super().__init__()
        self.ptr_depth = 0
        self.stack_size = 1
        self.kind = None
        self.ident = None
        self.expr = None

    def attributes_tostr(self):
        return f" ptr_depth=\"{self.ptr_depth}\" stack_size=\"{self.stack_size}\""

    def content_tostr(self, indent):
        result = f"{' ' * (indent)}{self.kind}\n"
        result += f"{' ' * (indent)}{self.ident}\n"
        if self.expr != None:
            result += self.expr.tostr(indent)

        return result


class Literal(Expr):
    def __init__(self):
        super().__init__()
        self.token = None
        self.offset = None

    def attributes_tostr(self):
        return f" offset=\"{self.offset}\""

    def content_tostr(self, indent):
        return f"{' ' * indent}{self.token}\n"


class UnaryOp(Expr):
    def __init__(self):
        super().__init__()
        self.op = None
        self.expr = None

    def content_tostr(self, indent):
        result = f"{' ' * (indent)}{self.op}\n"
        result += self.expr.tostr(indent)
        return result


class BinaryOp(Expr):
    def __init__(self):
        super().__init__()
        self.op = None
        self.lhs = None
        self.rhs = None

    def content_tostr(self, indent):
        result = f"{' ' * (indent)}{self.op}\n"
        result += self.lhs.tostr(indent)
        result += self.rhs.tostr(indent)
        return result
