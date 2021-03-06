#!/usr/bin/env python
# -*- coding: utf-8 -*-

import analyze
import sys, os

import files

import builtin
import operators
import libintp

import objects.about

from objects.orobject import OrObject
from objects.inheritdict import InheritDict
from objects.module import Module
import objects.number
import objects.constants

class ContinueI(Exception): pass
class BreakI(Exception): pass
class PyDropI(Exception): pass
class DropI(Exception): pass

def str_to_bool(s):
    return s.lower() not in ("false", "off", "no", "bad", "never", "death", "evil", "red", "door")

def flatten_tuples(s, l=None):
    if l is None:
        l = []

    for i in s:
        if type(i) == type(()) or hasattr(i, "ispy") and i.ispy() and type(i.topy()) == type(()):
            flatten_tuples(i, l)
        else:
            l.append(i)

    return l

def autoblock(f):
    def t(self, *args, **kwargs):
        if self.opts["debugger"]:
            self.opts["debugger"].steplevel += 1
        try:
            v = f(self, *args, **kwargs)
        finally:
            if self.opts["debugger"]:
                self.opts["debugger"].steplevel -= 1
        return v
    return t

class Interpreter(object):
    curr = property(lambda self: self.cntx[-1])
    
    repl_hook = lambda self: None
    debug_hook = lambda self, fname, lineno, line: None

    def register(self, t, name, function):
        if str(t).lower() in ("procdir", "dir", "directive", "processing directive"):
            self.procdirs[str(name)] = function
        else:
            self.procblocks[str(name)] = function

    def quit(self):
        sys.exit()

    def __str__(self):
        return "<Interpreter intp>"

    def __repr__(self):
        return str(self)
    
    def __init__(self, g=None):

        # Set up the global contexts
        if not g:
            g = InheritDict(builtin.builtin)
        self.cntx = [g, InheritDict(g)]
        self.bindcntx = self.cntx[-1]
        self.curr["intp"] = OrObject.from_py(self)

        # Set up interpreter options
        self.opts = {"logger": None, "debugger": None}

        # Set up statement stacks and location information
        self.stmtstack = []
        self.cstmt = [(0, 0), (0, 0), ""] # Default
        self.level = 0
        self.consolelevel = 0

        # Set up module search path
        self.searchpath = [files.Path("."), files.Path(objects.about.mainpath) +
            "../stdlib", files.Path(objects.about.mainpath) + "../sitelib"]
        userbase = files.Path("%APPDATA%/oranj/" if os.name == "nt" else
            "~/.local/lib/oranj")
        self.searchpath.append(userbase)
        self.searchpath.append(userbase + objects.about.version)

        # A few convenience methods for dealing with variables
        @OrObject.from_py
        def vars():
            return OrObject.from_py(self.curr.dict)

        @OrObject.from_py
        def globals():
            return OrObject.from_py(self.cntx[1].dict)

        @OrObject.from_py
        def locals():
            return OrObject.from_py(self.curr.dict)

        g["vars"] = vars
        g["globals"] = globals
        g["locals"] = locals

        import libproc
        self.procblocks = libproc.blocks
        self.procdirs = libproc.dirs
    
    def quit():
        sys.exit()

    # For setting some options
    def set_option(self, opt, val):
        if opt == "ec": # Turn activity log on or off
            if str_to_bool(val):
                import errorcontext
                self.opts["logger"] = errorcontext.ErrorContext()
            else:
                if self.opts["logger"] is not None:
                    self.opts["logger"].active = False
        elif opt == "path":
            self.searchpath.append(files.Path(val))

    def run(self, tree):
        if len(tree) and type(tree[0]) == type(""):
            return Interpreter.__dict__["h" + tree[0]](self, *tree[1:])
        else:
            j = objects.constants.nil
            for i in tree:
                if self.opts["debugger"] and self.opts["debugger"].check() and \
                        i[0] == "STATEMENT":
                    self.opts["debugger"].debug(i[1][0], i[3])
                j = self.run(i)
            return j

    @autoblock
    def hFOR(self, (names, vals), block):
        vals = map(self.run, vals)
        valpairs = zip(*vals)

        for v in valpairs:
            for n, vv in zip(names, flatten_tuples(v)):
                self.curr[n] = OrObject.from_py(vv)
            self.run(block)

        return zip(valpairs)

    @autoblock
    def hFOR2(self, (names, vals), block, *others):
        vals = map(self.run, vals)
        valpairs = zip(*vals)

        try:
            for v in zip(*vals):
                try:
                    for n, vv in zip(names, flatten_tuples(v)):
                        self.curr[n] = OrObject.from_py(vv)
                    self.run(block)
                except ContinueI, e:
                    if e.args != () and e.args[0] > 1:
                        v = e.args[0] - 1
                        raise ContinueI(v)
        except BreakI, e:
            if e.args != () and e.args[0] != 0:
                v = e.args[0] - 1
                raise BreakI(v)
            else:
                if "ELSE" in others:
                    i = others.find("ELSE")
                    self.run(others[i + 1])
        
        return valpairs

    def hSTATEMENT(self, linespan, charspan, txt, val):
        self.level += 1
        self.cstmt = [linespan, charspan, txt]
        self.stmtstack.append(self.cstmt)
        asdf = self.run(val)
        self.stmtstack.pop()
        self.level -= 1
        return asdf

    def hLIST(self, vars):
        return OrObject.from_py(map(self.run, vars))

    def hDICT(self, vars):
        vars = map(lambda x: (self.run(x[0]), self.run(x[1])), vars)
        return OrObject.from_py(dict(vars))

    def hSLICE(self, *stops):
        return OrObject.from_py(slice(*[self.run(i).topy() for i in stops]))

    def hIDENT(self, var):
        if var in self.curr:
            return self.curr[var]

        for c in self.cntx[:-1:-1]:
            if var in c:
                return c[var]

        raise NameError("`%s` is not defined" % var)

    def hPROCDIR(self, cmd):
        args = cmd[1:]
        cmd = cmd[0]
        
        if cmd in self.procdirs:
            return OrObject.from_py(self.procdirs[cmd](args, self, globals()))
        elif cmd == "set":
            if len(args) != 2:
                raise SyntaxError("#!set requires two arguments")

            return self.set_option(args[0], args[1])
        elif cmd == "debug":
            if not self.opts["debugger"]:
                import debugger
                self.opts["debugger"] = debugger.Debugger(self, ":anon:")

            self.opts["debugger"].stepconsole = self.consolelevel
            self.opts["debugger"].steplevel = self.level
            return
        elif cmd == "step":
            self.opts["debugger"].steplevel += 1
            if args[0] == "in":
                self.opts["debugger"].steplevel += 2
            elif args[0] == "out":
                self.opts["debugger"].steplevel -= 2
            elif args[0] == "end":
                self.opts["debugger"].steplevel = -1

            raise DropI("Stepping")
        elif cmd == "ec":
            if not self.opts["logger"]:
                return
            elif not args:
                return OrObject.from_py(self.opts["logger"])
            elif len(args) >= 1 and args[0] == "data":
                type = "data"
                val = " ".join(args[1:])
            else:
                type = "message"
                val = " ".join(args)
            
            return self.opts["logger"].write(val, type)

        # Hmm, we still haven't been run
        raise SyntaxError("Processing directive not available: " + cmd)

    def hPROCBLOCK(self, type, body):
        if type[0] in self.procblocks:
            fn = self.procblocks[type[0]]
            return OrObject.from_py(fn(type[1:], body, self, globals()))
        else:
            raise SyntaxError("Processing block not available: " + type[0])
        
    def hPRIMITIVE(self, val, *others):
        if val[0] in ("DEC", "INT"):
            return objects.number.Number(*val[1:])
        elif val[0] == "BOOL":
            return OrObject.from_py(val[1])
        elif val[0] == "NIL":
            return OrObject.from_py(None)
        elif val[0] == "INF":
            return objects.constants.inf

    def hSTRING(self, vals):
        strs = []
        for val in vals:
            body, flags = val[1:]
            if "r" not in flags:
                body = eval('"""' + body + '"""')
            strs.append(body)
        return OrObject.from_py("".join(strs))

    def hASSIGN(self, idents, vals):
        vals = [["VALUE", self.run(val)] for val in vals]
        for i, v in zip(idents, vals):
            self.hASSIGN1(i, v)
        return map(lambda val: val[1], vals)

    def hASSIGN1(self, ident, val):
        val = self.run(val)

        if type(ident) == type(""):
            self.curr[ident] = val
            if val.get("$$name") == "[anon]":
                val.set("$$name", ident)
        elif ident[0] == "SETATTR":
            self.run(ident[1]).set(ident[2], val)
        elif ident[0] == "SETINDEX":
            self.run(ident[1])[self.run(ident[2])] = val
        return val

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
        return self.curr[i]

    def hGETATTR(self, var, id):
        var = self.run(var)
        return operators.getattr_(var, id)

    def hASSERT(self, val, doc=""):
        val = self.run(val)
        if val:
            return val

        if doc:
            raise AssertionError
        else:
            raise AssertionError(self.run(doc))

    def hOP1(self, op, v1, v2):
        return OrObject.from_py(operators.op_names[op](self.run(v1), self.run(v2)))
        
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

        return OrObject.from_py(r)

    @autoblock
    def hIF(self, cond, body, *others):
        if self.run(cond):
            return self.run(body)
        else:
            for i, v in enumerate(others[::3]):
                if v == "ELIF":
                    if self.run(others[i + 1]):
                        return self.run(others[i + 2])
                    return
                else:
                    return self.run(others[i + 1])

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

    @autoblock
    def hWHILE(self, cond, body, *others):
        if cond:
            test = lambda:  self.run(cond)
        else:
            test = lambda: True

        while test():
            self.run(body)
        return constants.objects.true

    @autoblock
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
        except BreakI, e:
            if e.args and e.args[0] > 1:
                raise BreakI(e.args[0] - 1)
            else:
                return objects.constants.false
        return objects.constants.true

    def hCALL(self, val, *args):
        func = self.run(val)
      
        if func.tagged("FullMacro") or func.tagged("Macro"):
            # Eh, don't shoot yourself in the foot
            a = map(OrObject.from_py, args)
            kw = {}
        else:
            a = []
            kw = {}

            for i in args:
                if i[0] == "UNWRAPKW":
                    kw.update(self.run(i[1]))
                elif i[0] == "KW":
                    kw[i[1]] = self.run(i[2])
                elif i[0] == "UNWRAP":
                    a.extend(self.run(i[1]).topy())
                else:
                    a.append(self.run(i))
        
        try:
            r = operators.call(func, *a, **kw)
        finally:
            if self.level > len(self.stmtstack):
                self.stmtstack = self.stmtstack[:self.level]
        
        if func.tagged("FullMacro"):
            r = self.run(r)

        if not isinstance(r, OrObject):
            return OrObject.from_py(r)
        else:
            return r

    @autoblock
    def hTRY(self, block, *catches):
        try:
            self.run(block)
            return objects.constants.true
        except Exception, e:
            for i, v in enumerate(catches[1::4]):
                if any(operators.is_(e, self.run(j)) for j in v) or not v:
                    if catches[3*i+2]:
                        self.curr[catches[3*i+2]] = OrObject.from_py(e)
                    self.run(catches[3*i+3])
                    return objects.constants.false

            if catches[-2] == "FINALLY":
                self.run(catches[-1])

            raise

    @autoblock
    def hCLASS(self, doc, parents, tags, block):
        from objects.orclass import OrClass
        return OrClass(self, map(self.run, parents), tags, block, self.run(doc) if doc else "")

    def __get_import_loc(self, path):
        for loc in self.searchpath:
            if path[0] in loc or path[0] + ".or" in loc:
                return loc
        raise ImportError("Module %s not found" % ".".join(path))

    def __get_py_import(self, path):
        flag = False
        sys.path.append(str(files.Path(objects.about.mainpath) + ".."))
        
        for i in range(len(path)):
            p = path[0] + "_or." + ".".join(["pystdlib"] + path[:i+1])
            
            try:
                __import__(p)
            except ImportError:
                break
            else:
                val = sys.modules[p]
                flag = True
        else:
            i += 1
        
        sys.path.pop()
        
        if flag:
            return val, i+1

        flag = False
        for i in range(len(path)):
            p = ".".join(path[:i+1])
            try:
                __import__(p)
            except ImportError, e:
                break
            else:
                val = sys.modules[p]
                flag = True
        else:
            i += 1

        if flag:
            return val, i
        
        if i == 0:
            raise ImportError("Module %s not found" % ".".join(path))
        else:
            return val, i

    @autoblock
    def hIMPORT(self, path, fname="", vars=[]):

        #Step 1: Get module
        try:
            if path[0] == "py":
                path = path[1:]
                raise ImportError # Skip to except clause
            
            loc = self.__get_import_loc(path)
        except ImportError:
            try:
                v, pathp = self.__get_py_import(path)
            except ImportError:
                raise ImportError("Module %s not found" % ".".join(path))
            else:
                name = path[pathp - 1]
                mod = Module.from_py(v)
        else:
            pathp = 0
            while pathp < len(path) and (loc + path[pathp]).exists():
                loc += path[pathp]
                pathp += 1

            if pathp < len(path) and (loc + (path[pathp] + ".or")).exists():
                loc += path[pathp] + ".or"
                pathp += 1

            if "file" in loc.type():
                f = loc.get().open().read()
            elif "$$init.or" in loc:
                f = (loc+"$$init.or").get().open()
            else:
                f = ""
                
            intp2 = Interpreter()
            
            for i in vars:
                intp2.curr[i[2]] = self.curr[i[2]]
                
            run(f, intp2)
            name = path[pathp - 1]
            mod = Module(intp2.curr.dict, name, str(loc))

        # OK, done. mod is now a module object
        for i in path[pathp:]:
            if i != "*":
                try:
                    mod = mod.get(i)
                    name = i
                except KeyError:
                    raise ImportError("Module %s not found" % ".".join(path))
            else:
                for i in mod.dict:
                    self.curr[i] = OrObject.from_py(mod.dict.get(i))
                return

        fname = fname if fname else name

        self.curr[name] = OrObject.from_py(mod)
        return self.curr[name]

    def hVALUE(self, val):
        return val

def run(s, intp=None, **kwargs):
    if intp is None:
        intp = Interpreter()

    for i in kwargs:
        intp.curr[i] = kwargs[i]

    return intp.run(analyze.parse(s))

builtin.builtin["eval"] = builtin.expose(run, "eval")

