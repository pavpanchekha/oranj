from orobject import OrObject
from function import Function
import types

class File(OrObject):
    def __init__(self, fname, mode="r"):
        OrObject.__init__(self)
        self.set("$$class", "File")
        self.set("$$input", Function.new(self.input))
        self.set("$$output", Function.new(self.output))
        self.set("read", Function.new(self.read))
        self.set("write", Function.new(self.write))


        if type(fname) == type(""):
            self.fname = fname
            self.file = open(fname, mode)
        elif type(fname) == types.FileType:
            self.fname = "???"
            self.file = fname
        
        for i in dir(self.file):
            if not i.startswith("__") and i not in self.dict:
                self.set(i, OrObject.from_py(getattr(self.file, i)))
        
        self.buf = []

    def ispy(self): return False
    def topy(self): return NotImplemented

    def __str__(self):
        return "<File " + self.fname + ">"

    def input(self, validator):
        return self.read(validator)

    def output(self, arg):
        self.write(arg, sep="", end="")

    def read(self, valid_f=None, coerce_f=None):
        if valid_f is None and coerce_f is None:
            return file.read()
        else:
            if not self.buf:
                a = self.file.readline()[:-1].split()
                self.buf.extend(a[1:])
                txt = a[0]
            else:
                txt = self.buf.pop(0)

        if coerce_f is None:
            try:
                return valid_f(txt)
            except:
                self.buf.append(txt)
                raise IOError("Wrong input format")
        else:
            try:
                if not valid_f(txt):
                    raise Exception
            except:
                self.buf.append(txt)
                raise IOError("Wrong input format")
            else:
                return coerce_f(txt)

    def write(self, *args, **kwargs):
        p = {
            "sep": " ",
            "end": ""
        }

        p.update(kwargs)

        sep = p["sep"]
        end = p["end"]

        try:
            self.file.write(sep.join(map(str, args)))
            self.file.write(str(end))
        except:
            raise IOError("File not open in write or append mode")
        
        return self

OrObject.register(File, types.FileType)
