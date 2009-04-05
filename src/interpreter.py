#!/usr/bin/env python

import analyze
import sys

import builtin
import intplib
from objects.orobject import OrObject
import objects.number as number
import objects.orddict as odict
import objects.orclass as orclass

from objects.inheritdict import InheritDict

class ContinueI(Exception): pass
class BreakI(Exception): pass
class DropI(Exception): pass

class Interpreter(object):
    curr = property(lambda self: self.cntx[-1])
    run_console = None

    def __init__(self, g=None):
        if not g:
            g = InheritDict(builtin.builtin)
        
        self.cntx = [g, InheritDict(g)]
        self.types = {}

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

    def hLIST(self, vars):
        return OrObject.from_py(map(self.run, vars))

    def hSET(self, vars):
        return OrObject.from_py(set(map(self.run, r)))
    
    def hTABLE(self, vars):
        vars = map(lambda x: (self.run(x[0]), self.run(x[1])), vars)
        return odict.ODict(vars)

    def hDICT(self, vars):
        vars = map(lambda x: (self.run(x[0]), self.run(x[1])), vars)
        return OrObject.from_py(dict(vars))

    def hSLICE(self, *stops):
        return OrObject.from_py(slice(*[self.run(i).topy() for i in stops]))
    
    def hIDENT(self, var):
        try:
            return self.curr[var]
        except AttributeError:
            raise AttributeError("Variable %s does not exist" % var)

    def hPROCDIR(self, cmd, *args):
        if cmd == "drop":
            Interpreter.run_console(self)
        elif cmd == "clear":
            intplib.clear_screen()
        elif cmd == "exit":
            sys.exit()
        elif cmd == "pydrop":
            raise DropI

    def hPROCBLOCK(self, type, body):
        glob = globals()
        glob["intp"] = self
        
        if type[0] == "python":
            exec body in glob, {}

    def hPRIMITIVE(self, val, *others):
        if val[0] == "STRING":
            body, flags = val[1:]
            if "r" not in flags:
                body = eval('"' + body + '"')
            return OrObject.from_py(body)
        elif val[0] in ("DEC", "INT"):
            return number.Number(*val[1:])
        elif val[0] == "BOOL":
            return OrObject.from_py(val[1])
        elif val[0] == "NIL":
            return OrObject.from_py(None)
        elif val[0] == "INF":
            return number.inf

    def hASSIGN(self, idents, vals):
        vals = map(self.run, vals)
        
        for i, v in zip(idents, vals):
            self.curr[i] = v
            if v.get("$$name") == "[anon]":
                v.set("$$name", i)
    
    def hASSIGN1(self, ident, val):
        val = self.run(val)
        self.curr[ident] = val
        if val.get("$$name") == "[anon]":
            val.set("$$name", ident)

    def hDECLARE(self, type, (idents, vals)):
        for i in idents:
            self.types[i] = type
            
        self.hASSIGN((idents, vals))

    def hFN(self, args, block, doc, rettype):
        return intplib.Function(self, args, block, doc, rettype)
    
    def hRETURN(self, *args):
        args = map(self.run, args)
        raise intplib.ReturnI(*args)
    
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
        return intplib.getattr_(var, id)

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
            if type(args[0]) == type(""): # IDENT++
                v = self.curr[args[0]]
                self.curr[args[0]] = intplib.add(self.curr[args[0]], number.Number(1 if op == "++" else -1))
                return v
            return


        args = map(self.run, args)
        func = intplib.op_names[op]

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
            test = lambda: self.run(cond)
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

            r = intplib.call(func, *a)
            if not isinstance(r, OrObject):
                return OrObject.from_py(r)
            else:
                return r

    def hTRY(self, block, *catches):
        try:
            self.run(block)
        except Exception, e:
            for i, v in enumerate(catches[1::4]):
                if any(intplib.is_(e, self.run(j)) for j in v) or not v:
                    if catches[3*i+2]:
                        self.curr[catches[3*i+2][1]] = OrObject.from_py(e)
                    self.run(catches[3*i+3])
                    return
            raise

    def hCLASS(self, doc, parents, tags, block):
        return orclass.OrClass(self, map(self.run, parents), tags, block, self.run(doc))

def run(s, intp=Interpreter()):
    return intp.run(analyze.parse(s))

builtin.builtin["eval"] = OrObject.from_py(run)
