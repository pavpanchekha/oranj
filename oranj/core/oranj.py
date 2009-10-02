#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import objects.about

sys.path.append(os.path.join(objects.about.mainpath, "core", "lib"))

import interpreter as intp
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
    import objects.orobject
    glob["OrObject"] = objects.orobject.OrObject
    glob["intp"] = i

def import_readline():
    try:
        import readline
        return readline
    except ImportError:
        return None

def wrap(fn, i, glob):
    try:
        fn()
    except intp.PyDropI:
        print "Dropping down to python console. Call undrop() to return."
        pydrop(i, glob)
    except intp.DropI:
        run_console(i, glob)
    except Exception, e:
        libintp.print_exception(e, i)    

def debug_hook(i, file, lineno, line):
    print "%s:%d:\t%s" % (os.path.basename(file), lineno, line.split("\n")[0])
    i.shell_hook()

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

def run_file(base_i, child, glob):
    text = open(child[0]).read()
    if text.strip() != "":
        #wrap(lambda: intp.run(text, base_i), base_i, glob)
        intp.run(text, base_i)
        cli.run(base_i, child[1:], wrap)

def main(glob):
    intp.Interpreter.shell_hook = lambda x: run_console(x, glob)
    intp.Interpreter.debug_hook = debug_hook
    base_i = intp.Interpreter()
    kwargs = parse_args()

    if len(kwargs["child"]) and "test" not in kwargs:
        run_file(base_i, kwargs["child"], glob)
    elif "stdin" in kwargs:
        wrap(lambda: intp.run(sys.stdin.read(), base_i), base_i, glob)
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
    main(globals())
