# -*- coding: utf-8 -*-
from orobject import OrObject
from function import Function
import sys

class Console(OrObject):
    def __init__(self, fin=sys.stdin, fout=sys.stdout, ferr=sys.stderr):
        OrObject.__init__(self, "cons", Console)
        self.set("$$input", self.input)
        self.set("$$output", self.output)
        self.set("read", Function(self.read))
        self.set("write", Function(self.write))
        self.set("error", Function(self.error))

        self.fin = fin
        self.fout = fout
        self.ferr = ferr

    def ispy(self): return False
    def topy(self): return NotImplemented

    def __str__(self):
        return "<Console>"

    def input(self, validator):
        return self.read("", validator.topy())

    def output(self, arg):
        self.write(arg, sep="", end="")

    def read(self, prompt="", valid_f=None, coerce_f=None):
        """
        Get user input, validate, and coerce it if necessary.

        prompt: User prompt
        valid_f: the validation function. Should throw exception if input is invalid
        coerce_f: the coersion function. Should return coerced value.

        If only one function is passed (valid_f is given, coerce_f is not),
        valid_f is assumed to return coerced value.
        """

        if hasattr(prompt, "ispy") and prompt.ispy():
            prompt = prompt.topy()

        self.fout.write(prompt)
        txt = self.fin.readline()[:-1]

        if valid_f is None and coerce_f is None:
            return txt
        elif coerce_f is None:
            try:
                v = valid_f(txt)
                assert v != NotImplemented
                return v
            except:
                print "Invalid input; please try again."
                return input(prompt, valid_f, coerce_f)
        else:
            try:
                assert valid_f(txt) != NotImplemented
            except:
                print "Invalid input; please try again."
                return input(prompt, valid_f, coerce_f)
            else:
                return coerce_f(txt)

    def write(self, *args, **kwargs):

        p = {
            "sep": " ",
            "end": "\n"
        }

        p.update(kwargs)

        sep = p["sep"]
        end = p["end"]

        self.fout.write(sep.join(map(str, args)))
        self.fout.write(str(end))

    def error(self, *args):
        self.ferr.write("\n".join(map(str, args)) + "\n")

class IO(OrObject):
    def __init__(self, **binds):
        OrObject.__init__(self, "io", IO)
        self.__bound = binds
        self.bind(binds.items()[0][0])

        self.set("$$input", self.input)
        self.set("$$output", self.output)
        self.set("read", Function(self.read))
        self.set("write", Function(self.write))
        self.set("error", Function(self.error))
        self.set("bind", Function(self.bind))
        self.set("register", Function(self.register))
        self.set("get", Function(self.get_reg))

    def ispy(self): return False
    def topy(self): return NotImplemented

    def bind(self, key):
        if hasattr(key, "ispy") and key.ispy():
            key2 = key.topy()
        else:
            key2 = key

        try:
            self.__curr = self.__bound[key2]
        except KeyError:
            self.register(key)

    def register(self, s, v=None):
        if not v:
            v = s
            s = "[temp]"

        if hasattr(s, "ispy") and s.ispy():
            s = s.topy()

        self.__bound[s] = v
        self.bind(s)

    def get_reg(self, key=None):
        if not key:
            return self.__curr

        if hasattr(key, "ispy") and key.ispy():
            key = key.topy()

        return self.__bound[key]

    def read(self, *args, **kwargs):
        return self.__curr.get("read")(*args, **kwargs)

    def write(self, *args, **kwargs):
        self.__curr.get("write")(*args, **kwargs)
        return self

    def error(self, *args, **kwargs):
        return self.__curr.get("error")(*args, **kwargs)

    def input(self, *args, **kwargs):
        return self.__curr.get("$$input")(*args, **kwargs)

    def output(self, *args, **kwargs):
        self.__curr.get("$$output")(*args, **kwargs)
        return self

    def __str__(self):
        return "<io bound to " + repr(self.__curr) + ">"

io = IO(cons=Console())

def input(*args, **kwargs):
    return io.read(*args, **kwargs)

def output(*args, **kwargs):
    io.write(*args, **kwargs)

def error(*args, **kwargs):
    io.error(*args, **kwargs)
