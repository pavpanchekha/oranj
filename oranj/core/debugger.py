class Debugger(object):
    def __init__(self, intp, file=":anon:"):
        self.steplevel = -1
        self.stepconsole = -1
        self.file = file
        self.intp = intp

    def check(self):
        return self.steplevel > self.intp.level and self.stepconsole >= self.intp.consolelevel

    def debug(self, lineno, line):
        self.intp.debug_hook(self.file, lineno, line)


