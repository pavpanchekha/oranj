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

import cli

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
    args = cli.CLIArgs()
    args.mandatory = ["self", "child"]
    args.long = {"stdin": "bool", "test": "str", "self": "str"}
    args.short = {"": "stdin", "t": "test"}
    args.dump = "child"
    
    kwargs = cli.parseargs(sys.argv, args)
    
    kwargs = dict((k, v.topy()) for (k, v) in kwargs.items())

    return kwargs

def run_file(base_i, child):
    text = open(child[0]).read()
    if text.strip() != "":
        intp.run(text, base_i)
        cli.run(base_i, child[1:])

def main(glob):
    intp.Interpreter.run_console = lambda x: run_console(x, glob)
    base_i = intp.Interpreter()
    kwargs = parse_args()

    if len(kwargs["child"]) and "test" not in kwargs:
        run_file(base_i, child)
    elif "stdin" in kwargs:
        intp.run(sys.stdin.read())
    elif "test" in kwargs:
        import_readline()
        if kwargs["test"] == "a":
            import analyze
            analyze._test(kwargs["child"][0] if len(kwargs["child"]) > 0 else None)
        elif kwargs["test"] == "p":
            import parser
            parser._test(kwargs["child"][0] if len(kwargs["child"]) > 0 else None)
        elif kwargs["test"] == "l":
            import lexer
            lexer._test(kwargs["child"][0] if len(kwargs["child"]) > 0 else None)
    else:
        run_console(base_i, glob)

if __name__ == "__main__":
    main()
