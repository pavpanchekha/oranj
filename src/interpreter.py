#!/usr/bin/env python
# -*- coding: utf-8 -*-

import analyze
import sys

import builtin
import operators
import libintp

from objects.orobject import OrObject
from objects.inheritdict import InheritDict
import objects.number

class ContinueI(Exception): pass
class BreakI(Exception): pass
class PyDropI(Exception): pass
class DropI(Exception): pass

def str_to_bool(s):
    s = s.lower()

    return s not in ("false", "off", "no", "bad", "never", "death", "laplacian")

class Interpreter(object):
    curr = property(lambda self: self.cntx[-1])
    run_console = lambda self: None

    def __init__(self, g=None):
        if not g:
            g = InheritDict(builtin.builtin)

        self.cntx = [g, InheritDict(g)]
        self.types = {}

        self.opts = {
            "logger": None
            }
        
        self.stmtstack = []
        self.cstmt = [(0, 0), (0, 0), ""]
        self.level = 0

    def set_option(self, opt, val):
        if opt == "ec": # Turn activity log on or off
            if val:
                import errorcontext
                self.opts["logger"] = errorcontext.ErrorContext()
            else:
                if self.opts["logger"] is not None:
                    self.opts["logger"].active = False

    def run(self, tree):
        if not tree: return

        try:
            return getattr(self, "h" + tree[0])(*tree[1:])
        except:
            if type(tree[0]) == type("") and hasattr(self, "h" + tree[0]):
                raise

        if type(tree[0]) == type([]):
            for i in tree:
                j = self.run(i)
            return j
        elif tree[0] == "FOR":
            vals = map(self.run, tree[1][1])
            names = tree[1][0]

            for v in zip(*vals):
                for n, vv in zip(names, v):
                    self.curr[n] = OrObject.from_py(vv)
                self.run(tree[2])
        elif tree[0] == "FOR2":
            vals = map(self.run, tree[1][1])
            names = tree[1][0]

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

    def hSTATEMENT(self, linespan, charspan, txt, val):
        self.level += 1
        self.cstmt = [linespan, charspan, txt]
        self.stmtstack.append(self.cstmt)
        asdf = self.run(val)
        self.stmtstack.pop()
        self.level -= 1
        return asdf

    def hRAW(self, val):
        return val

    def hLIST(self, vars):
        return OrObject.from_py(map(self.run, vars))

    def hSET(self, vars):
        return OrObject.from_py(set(map(self.run, r)))

    def hTABLE(self, vars):
        from objects.orddict import ODict
        
        vars = map(lambda x: (self.run(x[0]), self.run(x[1])), vars)
        return ODict(vars)

    def hDICT(self, vars):
        vars = map(lambda x: (self.run(x[0]), self.run(x[1])), vars)
        return OrObject.from_py(dict(vars))

    def hSLICE(self, *stops):
        return OrObject.from_py(slice(*[self.run(i).topy() for i in stops]))

    def hIDENT(self, var):
        for c in self.cntx:
            try:
                i = c[var]
            except KeyError:
                pass
        
        try:
            return i
        except NameError:
            raise NameError("Variable %s does not exist" % var)

    def hPROCDIR(self, cmd, args=""):
        if cmd == "drop":
            Interpreter.run_console(self)
        elif cmd == "undrop":
            raise DropI
        elif cmd == "clear":
            libintp.clear_screen()
        elif cmd == "exit":
            sys.exit()
        elif cmd == "pydrop":
            raise PyDropI
        elif cmd == "pyerror":
            import traceback
            traceback.print_exc()
        elif cmd == "set":
            args = args.split()
            if len(args) != 2:
                raise SyntaxError("#!set requires two arguments")

            self.set_option(args[0], str_to_bool(args[1]))
        elif cmd == "ec":
            if not args or not self.opts["logger"]:
                return
            if len(args) >= 4 and args[:4] == "data" and args[4].isspace():
                type = "data"
                val = args[4:].strip()
            else:
                type = "message"
                val = args
            self.opts["logger"].write(val, type)
        elif cmd == "ecsave":
            if not args:
                raise SyntaxError("#ecsave requires variable name as argument")
            else:
                self.curr[args] = OrObject.from_py(self.opts["logger"])

    def hPROCBLOCK(self, type, body):
        glob = globals()
        glob["intp"] = self

        if type[0] == "python":
            exec body in glob, {}

    def hPRIMITIVE(self, val, *others):
        if val[0] in ("DEC", "INT"):
            return objects.number.Number(*val[1:])
        elif val[0] == "BOOL":
            return OrObject.from_py(val[1])
        elif val[0] == "NIL":
            return OrObject.from_py(None)
        elif val[0] == "INF":
            return objects.number.inf

    def hSTRING(self, vals):
        strs = []
        for val in vals:
            body, flags = val[1:]
            if "r" not in flags:
                body = eval('"' + body + '"')
            strs.append(body)
        return OrObject.from_py("".join(strs))

    def hASSIGN(self, idents, vals):
        for i, v in zip(idents, vals):
            self.hASSIGN1(i, v)

    def hASSIGN1(self, ident, val):
        val = self.run(val)

        if type(ident) == type(""):
            self.curr[ident] = val
            if val.get("$$name") == "[anon]":
                val.set("$$name", ident)
        elif ident[0] == "SETATTR":
            self.run(ident[1]).set(ident[2], val)
        elif ident[0] == "SETINDEX":
            self.run(ident[1])[ident[2]] = val

    def hDECLARE(self, type, (idents, vals)):
        for i in idents:
            self.types[i] = type

        self.hASSIGN((idents, vals))

    def hFN(self, args, block, doc, tags):
        return libintp.Function(self, args, block, self.run(["STRING", doc]), tags)

    def hRETURN(self, *args):
        args = map(self.run, args)
        raise libintp.ReturnI(*args)

    def hDEL(self, *vars):
        for i in vars:
            i = i[1]
            if i not in self.curr:
                raise NameError(i + " is not a valid variable")
            del t[i]

    def hEXTERN(self, *vars):
        for i in vars:
            if not self.curr.parent or i not in self.curr.parent:
                raise NameError(i + " is not a valid variable")
            self.curr[i] = self.curr.parent[i]

    def hGETATTR(self, var, id):
        var = self.run(var)
        return operators.getattr_(var, id)

    def hASSERT(self, val, doc=""):
        val = self.run(val)
        if val:
            return

        if doc:
            raise AssertionError
        else:
            raise AssertionError(self.run(doc))

    def hOP(self, op, *args):
        if op in ("--", "++"):
            v = self.run(args[0])
            self.hASSIGN1(analyze.parser.h_loc(args[0]), ["OP", op[0], args[0], ["PRIMITIVE", ("INT", "1", 10)]])
            return v

        args = map(self.run, args)
        func = operators.op_names[op]

        try:
            r = func(*args)
        except TypeError:
            raise

        if not isinstance(r, OrObject):
            return OrObject.from_py(r)
        else:
            return r

    def hIF(self, cond, body, *others):
        if self.run(cond):
            self.run(body)
        else:
            for i, v in enumerate(others[::3]):
                if v == "ELIF":
                    if self.run(tree[i + 1]):
                        self.run(tree[i + 2])
                    return
                else:
                    self.run(tree[i + 1])

    def hCONTINUE(self, val=None):
        if val:
            raise ContinueI(self.run(val).topy())
        else:
            raise ContinueI()

    def hBREAK(self, val=None):
        if val:
            raise BreakI(self.run(val).topy())
        else:
            raise BreakI()

    def hWHILE(self, cond, body, *others):
        if cond:
            test = lambda:  self.run(cond)
        else:
            test = lambda: True

        while test():
            self.run(body)
        else:
            if others:
                self.run(others[1])

    def hWHILE2(self, cond, body, *others):
        if cond:
            test = lambda: self.run(cond)
        else:
            test = lambda: True

        try:
            while test():
                try:
                    self.run(body)
                except ContinueI, e:
                    if e.args and e.args[0] > 1:
                        raise ContinueI(e.args[0] - 1)
                    else:
                        continue
            else:
                if others:
                    self.run(others[1])
        except BreakI, e:
            if e.args and e.args[0] > 1:
                raise BreakI(e.args[0] - 1)
            else:
                return

    def hCALL(self, val, *args):
        a = []
        kw = {}

        for i in args:
            if i[0] == "UNWRAPKW":
                kw.update(self.run(i[1]))
            elif i[0] == "KW":
                kw[self.run(i[1])] = self.run(i[2])
            elif i[0] == "UNWRAP":
                a.extend(self.run(i[1]).topy())
            else:
                a.append(self.run(i))

        func = self.run(val)
        try:
            r = operators.call(func, *a, **kw)
        finally:
            if self.level > len(self.stmtstack):
                self.stmtstack = self.stmtstack[:self.level]
        
        if not isinstance(r, OrObject):
            return OrObject.from_py(r)
        else:
            return r

    def hTRY(self, block, *catches):
        try:
            self.run(block)
        except Exception, e:
            for i, v in enumerate(catches[1::4]):
                if any(operators.is_(e, self.run(j)) for j in v) or not v:
                    if catches[3*i+2]:
                        self.curr[catches[3*i+2][1]] = OrObject.from_py(e)
                    self.run(catches[3*i+3])
                    return

            if catches[-2] == "FINALLY":
                self.run(catches[-1])

            raise

    def hCLASS(self, doc, parents, tags, block):
        from objects.orclass import OrClass
        return OrClass(self, map(self.run, parents), tags, block, self.run(doc))

def run(s, intp=Interpreter()):
    return intp.run(analyze.parse(s))

builtin.builtin["eval"] = OrObject.from_py(run)
