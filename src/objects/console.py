from orobject import OrObject
from function import Function
import sys
import functools

class Console(OrObject):
    def __init__(self, fin=sys.stdin, fout=sys.stdout, ferr=sys.stderr):
        OrObject.__init__(self)
        self.set("$$class", "Console")
        self.set("$$name", "cons")
        self.set("$$input", Function.new(self.input))
        self.set("$$output", Function.new(self.output))
        self.set("read", Function.new(self.read))
        self.set("write", Function.new(self.write))
        self.set("error", Function.new(self.error))

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
                return valid_f(txt)
            except:
                print "Invalid input; please try again."
                return input(prompt, valid_f, coerce_f)
        else:
            try:
                valid_f(txt)
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
        self.ferr.write("\n".join(map(repr, args)) + "\n")

class IO(OrObject):
    def __init__(self, **binds):
        OrObject.__init__(self)
        self.__bound = binds
        self.bind(binds.items()[0][0])

        self.set("$$name", "io")
        self.set("$$class", "IO")
        self.set("$$input", self.input)
        self.set("$$output", self.output)
        self.set("read", self.read)
        self.set("write", self.write)
        self.set("error", self.error)
        self.set("bind", Function.new(self.bind))
        self.set("register", Function.new(self.register))
        self.set("get", Function.new(self.get_reg))
        
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

    def get_reg(self, key):
        if hasattr(key, "ispy") and key.ispy():
            key = key.topy()
        
        return self.__bound[key]

    def read(self, *args, **kwargs):
        return self.__curr.get("read")(*args, **kwargs)

    def write(self, *args, **kwargs):
        return self.__curr.get("write")(*args, **kwargs)

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
    return io.write(*args, **kwargs)

def error(*args, **kwargs):
    return io.error(*args, **kwargs)