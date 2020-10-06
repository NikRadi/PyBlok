import sys


errors = []

def report_errors():
    print("Could not compile")
    for err in errors:
        err.filename = "Main.blk"
        print(err)


def report_exit():
    report_errors()
    sys.exit()


def add_err(line, msg):
    errors.append(CompileError(None, line, msg))


def add_err_exit(line, msg):
    add_err(line, msg)
    report_exit()


class CompileError:
    def __init__(self, filename, line, msg):
        self.filename = filename
        self.line = line
        self.msg = msg

    def __str__(self):
        return f"{self.filename}({self.line}) error: {self.msg}"