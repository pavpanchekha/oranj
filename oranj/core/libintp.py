#!/bin/false
# -*- coding: utf-8 -*-

from objects.function import Function, ReturnI
from objects.number import inf
import sys

import terminal
__term = terminal.TerminalController()

def clear_screen():
    import os
    if os.name == "posix":
        # Unix/Linux/MacOS/BSD/etc
        os.system('clear')
    elif os.name in ("nt", "dos", "ce"):
        # DOS/Windows
        os.system('CLS')
    else:
        # Fallback for other operating systems.
        print '\n' * 100


def str_exception(e, i):
    output = []
    output.append("${RED}%s${NORMAL}" % type(e).__name__ + \
        ("" if not e.args else (": " + str(e))))

    if i.opts["logger"] and i.opts["logger"].messages:
        output.append(str(i.opts["logger"]))
        i.opts["logger"].clear()
        output.append("")

    for q in i.stmtstack:
        output.append("Line %d%s (cols %d-%d): %s" % (q[0][0], q[0][1] if q[0][1] != q[0][0] else "", \
            q[1][0] + 1, q[1][1] + 1, q[2]))

    i.stmtstack = []        
    output.append(output[0])
    return "\n".join(output)

def print_exception(e, i):
    print >> sys.stderr, __term.render(str_exception(e, i))
