#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import objects.about

sys.path.append(os.path.join(objects.about.mainpath, "core", "lib"))

import interpreter as intp
from optparse import OptionParser
import traceback
import libintp
import parser

def pydrop(i, glob):
    import os
    os.environ["PYTHONINSPECT"] = "1"

    def undrop():
        run_console(i, glob)

    glob["undrop"] = undrop
    glob["intp"] = i

def import_readline():
    try:
        import readline
    except ImportError:
        return None

    def completer(text, state=0):
        if text:
            m = [i for i in intp.curr.keys() if i.startswith(text)]
        else:
            m = intp.curr.keys()[:]

        try:
            return m[state]
        except IndexError:
            return None

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    return readline

def run_console(i, glob):
    import lexer
    import analyze
    import_readline()
    i.consolelevel += 1

    try:
        t = ""
        while True:
            t = raw_input("oranj> ") + "\n"
            while not lexer.isdone(t):
                t += raw_input("     > ") + "\n"

            try:
                r = intp.run(t, i)
            except intp.PyDropI: raise
            except intp.DropI: raise EOFError
            except parser.ParseError: pass
            except Exception, e:
                libintp.print_exception(e, i)
            else:
                if hasattr(r, "isnil") and not r.isnil():
                    print repr(r)
    except EOFError, e:
        print
    except KeyboardInterrupt:
        print
        sys.exit()
    except intp.PyDropI:
        print "Dropping down to python console. Call undrop() to return."
        pydrop(i, glob)

    i.consolelevel -= 1

def parse_args():
    parser = OptionParser()
    parser.add_option("-r", "--readin", action="store_true", help="Read input from stdin until EOF, then execute it", default=False)
    parser.add_option("-t", "--test", help="Test a component (parser, lexer, analyzer). oranj -t p|l|a", default="")
    opts, args = parser.parse_args()
    child = []

    if args:
        child = sys.argv[sys.argv.index(args[0]):]
        opts = parser.parse_args(sys.argv[:sys.argv.index(args[0])])[0]

    return opts, args, child

def main(glob):
    intp.Interpreter.run_console = run_console
    base_i = intp.Interpreter()
    opts, args, child = parse_args()

    if child and not opts.test:
        text = open(child[0]).read()
        if text.strip() != "":
            intp.run(text, base_i)
            if "$$main" in base_i.curr:
                main = base_i.curr["$$main"]
                passargs = intp.OrObject.from_py(child)
                main(passargs)
    elif opts.readin:
        intp.run(sys.stdin.read())
    elif opts.test:
        import_readline()
        if opts.test == "a":
            import analyze
            analyze._test(child[0] if len(child) > 0 else None)
        elif opts.test == "p":
            import parser
            parser._test(child[0] if len(child) > 0 else None)
        elif opts.test == "l":
            import lexer
            lexer._test(child[0] if len(child) > 0 else None)
    else:
        run_console(base_i, glob)

if __name__ == "__main__":
    main()
