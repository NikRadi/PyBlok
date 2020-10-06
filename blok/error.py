

errors = []

def add_err(line, msg):
    errors.append(CompileError(None, line, msg))

class CompileError:
    def __init__(self, filename, line, msg):
        self.filename = filename
        self.line = line
        self.msg = msg

    def __str__(self):
        return f"{self.filename}({self.line}) error: {self.msg}"