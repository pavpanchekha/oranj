from oranj.supporting.pygments import OranjLexer as lexer

import src.interpreter as intp
import src.libintp
import src.lexer
import src.liblex
import re

name = "Oranj"
__letter = r"(?:\w|\$)"
word_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$"

def print_exception(e, i, write_callback=lambda: None):
    msg = "\x01r\x03%s\x04\x01d\x03%s\n" % (type(e).__name__, \
        ("" if not e.args else (": " + " ".join(map(str, e.args)))))

    write_callback(msg)

    if i.opts["logger"] and i.opts["logger"].messages:
        print str(i.opts["logger"])
        i.opts["logger"].clear()
        print ""

    for q in i.stmtstack:
        print "Line %d%s (cols %d-%d): %s" % (q[0][0], q[0][1] if q[0][1] != q[0][0] else "", \
            q[1][0] + 1, q[1][1] + 1, q[2])

    write_callback(msg)
    i.stmtstack = []

class Completer(object):
    reserved = src.liblex.reserved + ["true", "false", "nil", "inf"]
    
    def __init__(self, interp):
        self.interp = interp
        self.matches = []

    def complete(self, text, state):
        if "." in text:
            self.matches = self.attr_matches(text)
        elif "(" in text:
            pass
        else:
            self.matches = [i + ("(" if callable(v) else "") for i, v in self.interp.curr.items() if i.startswith(text)] + [i for i in Completer.reserved if i.startswith(text)]

class Interpreter(object):
    def __init__(self):
        self.interp = intp.Interpreter()
        self.syntaxerror_callback = None

    def eval(self, source):
        try:
            return intp.run(source, self.interp)
        except:
            return None

    def completer(self):
        return Completer(self.interp)
        
    def runsource(self, source):
        if not src.lexer.isdone(source):
            return True

        try:
            r = intp.run(source, self.interp)
        except intp.PyDropI:
            print "Unfortunately, #!pydrop is not supported in bpython at this time"
            # TODO: FIXME
        except intp.DropI: raise EOFError
        except src.parser.ParseError:
            if self.syntaxerror_callback is not None:
                self.syntaxerror_callback()
        except Exception, e:
            if hasattr(self, "write_callback"):
                print_exception(e, self.interp, self.write_callback)
            else:
                def pt(x):
                    print x
                print_exception(e, self.interp, pt)
        else:
            if hasattr(r, "isnil") and not r.isnil():
                print repr(r)
        return False

    def get_locals(self):
        return dict(self.interp.curr.items())
    locals = property(get_locals)

def prompt(more):
    if not more:
        return("\x01g\x03oranj> ", "oranj> ", "\x01g\x03oranj> \x04")
    else:
        return("\x01g\x03     > ", "     > ", "\x01g\x03     > \x04")

def complete_attrs(obj, expr, attr):
    result = ["%s.%s" % (expr, a) for a in obj.dict.keys() if a.startswith(attr)]
    return result
