#!/usr/bin/env python
# -*- coding: utf-8 -*-

import parser

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
        if type(i) != type([]) or len(i) == 0: continue
        if i[0] in ("+=", "-=", "^=", "/=", "//=", "*=", "mod=", "and=", "or=", "<<=", ">>="):
            for j in range(len(i[1])):
                i[2][j] = ["OP", i[0][:-1], augass_dostuff(i[1][j][:]), i[2][j]]
            i[0] = "ASSIGN"
        elif i[0] == "=":
            i[0] = "ASSIGN"

        get_augass(i)
    return

def op_op1(tree):
    for id, i in enumerate(tree):
        if type(i) != type([]) or len(i) == 0: continue
        if i[0] == "OP" and len(i) == 4:
            i[0] = "OP1"
        op_op1(i)

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
    p = parser.parse(t)

    get_augass(p)
    op_op1(p)
    check_break_continue(p)

    return p

def _test_run(s):
    import pprint

    global errors
    pprint.pprint(parse(s))

def _test(f):
    if not f:
        try:
            while True:
                _test_run(raw_input("analyze> ") + "\n")
        except (EOFError, KeyboardInterrupt):
            print
    else:
        _test_run(open(f).read())

if __name__ == "__main__":
    _test()
