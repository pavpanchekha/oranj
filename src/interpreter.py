import analyze
import sys
import lib
import decimal
import readline
import traceback

from intplib import OrObject, InheritDict, ContinueI, BreakI
import intplib

import lexer

class DropI(Exception): pass

debug = False

builtin = InheritDict()
builtin.update({
    "int": OrObject.from_py(lib.Integer),
    "term": OrObject.from_py(lib.term),
    "input": OrObject.from_py(lib.input),
    "output": OrObject.from_py(lib.output),
    "error": OrObject.from_py(lib.error),
    "Inputable": OrObject.from_py(lib.Inputable),
    "Outputable": OrObject.from_py(lib.Outputable),
    "Terminal": OrObject.from_py(lib.Terminal),
    "repr": OrObject.from_py(repr),
    "join": OrObject.from_py(lib.join),
})

class Interpreter(object):
    op_names = {
        "+": intplib.add,
        "-": intplib.sub,
        "*": intplib.mul,
        "^": intplib.exp,
        "/": intplib.div,
        "//": intplib.floor,
        "|": intplib.divis,
        "mod": intplib.mod,
        "OR": intplib.or_,
        "AND": intplib.and_,
        "NOT": intplib.not_,
        "IN": intplib.in_,
        "NOT IN": intplib.not_in,
        "IS": intplib.is_,
        "IS NOT": intplib.is_not,
        "<": intplib.lt,
        ">": intplib.gt,
        "<=": intplib.le,
        ">=": intplib.le,
        "=>": intplib.ge,
        "==": intplib.eq,
        "!=": intplib.ne,
        "<<": intplib.output,
        ">>": intplib.input,
        "U+": intplib.uplus,
        "U-": intplib.uminus,
        "CALL": intplib.call,
        "ATTR": intplib.getattr_,
        "INDEX": intplib.getindex_,
    }

    str_escapes = {
        r"\\": "\\",
        "\\\n": "",
        r"\'": "'",
        "\\\"": "\"",
        r"\a": "\a",
        r"\b": "\b",
        r"\f": "\f",
        r"\n": "\n",
        r"\r": "\r",
        r"\t": "\t",
        r"\v": "\v",
        # \N{xxx}
        # \uxxxx
        # \Uxxxxxxx
        # \ooo
        # \xhh
    }

    def __init__(self, g=InheritDict(builtin)):
        self.glob = g
        self.curr = InheritDict(self.glob)
        self.types = {}

    def run(self, tree):
        if type(tree) == type([]):
            j = OrObject.from_py(None)
            for i in tree:
                j = self.run(i)
            return j
        elif tree[0] == "IDENT":
            if tree[1] in self.curr:
                return self.curr[tree[1]]
            else:
                raise AttributeError("Variable " + tree[1] + " does not exist")
        elif tree[0] == "PROCDIR":
            if tree[1] == "drop":
                run_console(self)
            elif tree[1] == "clear":
                intplib.clear_screen()
            elif tree[1] == "pydrop":
                import os
                os.environ["PYTHONINSPECT"] = "1"
                raise DropI
        elif tree[0] == "PRIMITIVE":
            if tree[1][0] == "STRING":
                a = tree[1][1]
                for k, v in self.str_escapes.keys():
                    a = a.replace(k, v)
                return OrObject.from_py(a)
            elif tree[1][0] == "DEC":
                return OrObject.from_py(decimal.Decimal(tree[1][1]))
            elif tree[1][0] == "INT":
                return OrObject.from_py(int(tree[1][1], tree[1][2]))
            elif tree[1][0] == "BOOL":
                return OrObject.from_py(tree[1][1])
            elif tree[1][0] == "NIL":
                return OrObject.from_py(None)
            elif tree[1][0] == "INF":
                return OrObject.from_py(lib.Infinity)
            return None
        elif tree[0] == "SLICE":
            return OrObject.from_py(slice(*[self.run(i).get("$$python") for i in tree[1:]]))
        elif tree[0] == "LIST":
            r = []
            for i in tree[1]:
                r.append(self.run(i))
            return OrObject.from_py(r)
        elif tree[0] == "SET":
            r = set()
            for i in tree[1]:
                r.add(self.run(i))
            return OrObject.from_py(r)
        #TODO: TABLE
        elif tree[0] == "DICT":
            r = {}
            for i in tree[1]:
                r[self.run(i[0])] = self.run(i[1])
            return OrObject.from_py(r)
        elif tree[0] in ("+=", "-=", "^=", "/=", "//=", "*=", "mod=", "and=", "or=", "<<=", ">>=", "="):
            vals = map(self.run, tree[2])
            for i, v in zip(tree[1], vals):
                self.curr[i[1]] = v
        elif tree[0] == "DECLARE":
            for i in tree[2][1:]:
                self.types[i[0][1]] = tree[1]
            
            tree = tree[2]
            vals = map(self.run, tree[2])
            for i, v in zip(tree[1], vals):
                self.curr[i[1]] = v
        elif tree[0] == "DEL":
            for i in tree[1]:
                i = i[1]
                t = self.curr
                while i not in t.dict:
                    t = t.parent
                    if t == None:
                        raise NameError(i + " is not a valid variable")
                del t[i]
        elif tree[0] == "EXTERN":
            for i in tree[1]:
                i = i[1]
                t = self.curr
                while i not in t.dict:
                    t = t.parent
                    if t == None:
                        raise NameError(i + " is not a valid variable")
                self.curr[i] = t[i]
        elif tree[0] == "ASSERT":
            val = self.run(tree[1])
            if not val:
                if len(tree) == 2:
                    raise AssertionError
                else:
                    raise AssertionError(self.run(tree[2]))
        elif tree[0] == "IF":
            for i, v in enumerate(tree[::3]):
                if v in ("IF", "ELIF"):
                    val = self.run(tree[i + 1])
                    if val:
                        self.run(tree[i + 2])
                        return
                    else:
                        continue
                else:
                    self.run(tree[i + 1])
                    return
        elif tree[0] == "CONTINUE":
            if tree[1]:
                raise ContinueI(self.run(tree[1]).get("$$python"))
            else:
                raise ContinueI(1)
        elif tree[0] == "BREAK":
            if tree[1]:
                raise BreakI(self.run(tree[1]).get("$$python"))
            else:
                raise BreakI(1)
        elif tree[0] == "WHILE":
            if len(tree) >= 3 and tree[2] != "ELSE":
                test = lambda: self.run(tree[1])
                block = lambda: self.run(tree[2])
            else:
                test = lambda: True
                block = lambda: self.run(tree[1])
            
            try:
                while test():
                    try:
                        block()
                    except ContinueI, e:
                        if e.args != () and e.args[0] > 1:
                            v = e.args[0] - 1
                            raise ContinueI(v)
                        else:
                            continue
            except BreakI, e:
                if e.args != () and e.args[0] > 1:
                    v = e.args[0] - 1
                    raise BreakI(v)
                else:
                    if "ELSE" in tree:
                        i = tree.find("ELSE")
                        self.run(tree[i + 1])
        elif tree[0] == "FOR":
            vals = map(self.run, tree[1][1])
            names = map(lambda x: x[1], tree[1][0])

            try:
                for v in zip(*vals):
                    try:
                        for n, vv in zip(names, v):
                            self.curr[n] = OrObject.from_py(vv)
                        self.run(tree[2])
                    except ContinueI, e:
                        if e.args != () and e.args[0] > 1:
                            v = e.args[0] - 1
                            raise ContinueI(v)
            except BreakI, e:
                if e.args != () and e.args[0] != 0:
                    v = e.args[0] - 1
                    raise BreakI(v)
                else:
                    if "ELSE" in tree:
                        i = tree.find("ELSE")
                        self.run(tree[i + 1])
        elif tree[0] == "ATTR":
            v1 = self.run(tree[1])
            v2 = tree[2][1]
            return intplib.getattr_(v1, v2)
        elif tree[0] in self.op_names:
            args = []
            kwargs = {}
            for i in tree[2:]:
                if i[0] == "UNWRAPKW":
                    kwargs.update(self.run(i[1]).get("$$python"))
                    # TODO: remove dependence on python
                    # Applies to all
                elif i[0] == "KW":
                    kwargs[self.run(i[1])] = self.run(i[2])
                elif i[0] == "UNWRAP":
                    args.extend(self.run(i[1]).get("$$python"))
                else:
                    args.append(self.run(i[1]))
                
            args = [self.run(i) for i in tree[2:]]
            var = self.run(tree[1])
            func = self.op_names[tree[0]]
            
            if debug:
                print var, func, args, kwargs

            try:
                r = func(var, *args, **kwargs)
            except TypeError:
                raise
                raise TypeError("Unsupported opperation: " + tree[0])
            else:
                if not isinstance(r, OrObject):
                    r = OrObject.from_py(r)

                if tree[0] in ("<<", ">>"):
                    return var
                else:
                    return r

def run_console(intp):
    def completer(text, state=0):
        return [i for i in intp.curr.names if i.startswith(text)]
    
    readline.set_completer(completer)
    
    try:
        t = ""
        while t != "exit":
            t = raw_input("oranj> ") + "\n"
            while not lexer.isdone(t):
                t += raw_input("     > ") + "\n"

#                print t
            p = analyze.parse(t)

            try:
                r = intp.run(p)
                if r == None: pass
                elif isinstance(r, OrObject) and "$$python" in r.dict and r.get("$$python") == None: pass
                else:
                    print r
            except DropI: raise
            except Exception, e:
                traceback.print_exc()
    except (KeyboardInterrupt, EOFError):
        print
        sys.exit()
    except DropI:
        print "Dropping down to python console. Call undrop() to return."

def run(s, intp):
    try:
        intp.run(analyze.parse(s))
    except DropI:
        return

if __name__ == "__main__":
    intp = Interpreter(builtin)

    def undrop():
        run_console(intp)

    argv = sys.argv[:]
    if "-d" in argv:
        del argv[argv.index("-d")]
        debug = True
    
    if len(argv) > 1:
        if "-c" in argv:
            run(sys.stdin.read(), intp)
        else:
            #TODO: argument parsing code
            run(open(sys.argv[1]).read(), intp)
    else:
        run_console(intp)
