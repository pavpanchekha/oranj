#!/usr/bin/env python

import parser
import sys
import pprint

#import runtime

errors = 0

def get_augass(tree):
    for id, i in enumerate(tree):
        if type(i) not in (type(()), type([])) or len(i) == 0: continue
        if i[0] in ("+=", "-=", "^=", "/=", "//=", "*=", "mod=", "and=", "or=", "<<=", ">>="):
            for j in range(len(i[1])):
                i[2][j] = (i[0][:-1], i[1][j], i[2][j])
            i = list(i)
            i[0] = "="
            tree[id] = tuple(i)
        elif type(tree) in (type(()), type([])):
            get_augass(i)
    return

def check_flowcontroll(tree):
    inloop = 0
    infunc = 0

    def go(tree):
        if tree[0] in ("WHILE", "FOR"):
            inloop += 1
            go(tree[2])
            go(tree[4])
            inloop -= 1
        elif tree[0] == "FN":
            infunc += 1
            go(tree[-1])
            infunc -= 1
        elif tree[0] in ("BREAK", "CONTINUE") and not inloop:
            raise Exception("Invalid " + tree[0] + " statement")
        elif tree[0] in ("RETURN", "YIELD") and not infunc:
            raise Exception("Invalid " + tree[0] + " statement")

    go(tree)
    return

#TODO: Check types

def parse(t):
    try:
        p = parser.parse(t)
    except:
        raise

    get_augass(p)
    check_flowcontroll(p)

    return p

def _test(s):
    global errors
    y = parse(s)
    
    if type(y) == type([]) and len(y) > 1:
        errors += 1

    if errors:
        print term.render("${RED}${BOLD}%d error%s" % (errors, "s" if errors > 1 else ""))
    else:
        pprint.pprint(y[0])

if __name__ == "__main__":
    if len(sys.argv) == 2:
        y = parse(open(sys.argv[1]).read())
    else:
        try:
            while True:
                _test(raw_input("parse> "))
        except (EOFError, KeyboardInterrupt):
            print
