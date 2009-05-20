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

def print_exception(e, i):
    msg = __term.render("${RED}%s${NORMAL}" % type(e).__name__ + \
        ("" if not e.args else (": " + " ".join(map(str, e.args)))))

    print >> sys.stderr, msg

    if i.opts["logger"] and i.opts["logger"].messages:
        print >> sys.stderr, str(i.opts["logger"])
        i.opts["logger"].clear()
        print >> sys.stderr, ""

    for q in i.stmtstack:
        print >> sys.stderr, "Line %d%s (cols %d-%d): %s" % (q[0][0], q[0][1] if q[0][1] != q[0][0] else "", \
            q[1][0] + 1, q[1][1] + 1, q[2])

    print >> sys.stderr, msg
    i.stmtstack = []
