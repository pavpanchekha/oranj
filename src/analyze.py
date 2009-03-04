#!/usr/bin/env python

import parser
import sys
import pprint

#import runtime

errors = 0

def augass_dostuff(s):
    if type(s) == type(""):
        return ["IDENT", s]
    elif s[0] == "SETATTR":
        s[0] = "GETATTR"
        return s
    elif s[0] == "SETINDEX":
        s[0] = "GETINDEX"
        return s

def get_augass(tree):
    for id, i in enumerate(tree):
        if type(i) not in (type(()), type([])) or len(i) == 0: continue
        if i[0] in ("+=", "-=", "^=", "/=", "//=", "*=", "mod=", "and=", "or=", "<<=", ">>="):
            for j in range(len(i[1])):
                i[2][j] = ["OP", i[0][:-1], augass_dostuff(i[1][j]), i[2][j]]
            i[0] = "ASSIGN"
        elif i[0] == "=":
            i[0] = "ASSIGN"
        elif type(tree) in (type(()), type([])):
            get_augass(i)
    return

def check_break_continue(tree, lstack=[]):
    if len(tree) == 0 or type(tree) != type([]): return

    if tree[0] in ("WHILE", "FOR"):
        lstack.append(tree)

        for i in tree:
            if type(i) == type([]):
                check_break_continue(i)

        lstack.pop()
    elif tree[0] in ("BREAK", "CONTINUE"):
        if not lstack:
            raise Exception("Invalid " + tree[0] + " statement")

        if tree[1] and tree[1][0] == "PRIMITIVE" and tree[1][1][0] == "INT":            
            min = len(lstack) - int(tree[1][1][1], tree[1][1][2])
            
            for i, v in enumerate(lstack):
                if i >= min:
                    v[0] += "2"
        elif tree[1] == None:
            lstack[-1][0] += "2"
        else:
            for i in lstack:
                i[0] += "2"
    else:
        for i in tree:
            if type(i) == type([]):
                check_break_continue(i)

#TODO: Check types

def parse(t):
    try:
        p = parser.parse(t)
    except:
        raise

    get_augass(p)
    check_break_continue(p)

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
