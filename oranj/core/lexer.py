#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ply.lex as lex
import liblex
import re

tokens = [
    "STRING", "DEC", "INT", "BOOL", "NIL", "IDENT", "PLUSPLUS", "MINUSMINUS",
    "SLASHSLASH", "GE", "LE", "NE", "EQ", "LTLT", "GTGT", "DOTDOTDOT", "EQOP",
    "NEWLINE", "PROCDIR", "PROCBLOCK", "INF", "ISNT", "ASSIGN"
]

# WARNING: t_STRING ***must*** be first in the list of functions.
# Because otherwise \n will refer to something else.
# Oh, and add one to whatever subgroup you think you refer to.

def t_STRING(t):
    r"""[a-z]*((['"])(?:\3\3)?)(?:\\\3|[^\2])*?\2"""

    t.value = liblex.hSTRING(t.value)
    return t

def t_ISNT(t):
    r"(is\s+not)|(aint)"

    return t

def t_BOOL(t):
    r"true|false"

    t.value = liblex.hBOOL(t.value)
    return t

def t_NIL(t):
    r"nil"

    t.value = liblex.hNIL(t.value)
    return t

def t_INF(t):
    r"inf"

    t.value = liblex.hINF(t.value)
    return t

def t_INT2(t):
    r"""(?<![\.eE]|\d)(?:(?:[ \t]*[0-9])+)(?![ \t]*\.|\d|\w)"""

    t.value = liblex.hINT(t.value)
    t.type = "INT"
    return t

def t_INT(t):
    r"""(?<![\.eE]|\d)(?:0(?:\w))(?:(?:[ \t]*[0-9a-zA-Z])+)(?![ \t]*\.|\d|\w)"""

    t.value = liblex.hINT(t.value)
    return t

def t_DEC(t):
    r"(?P<number>(?:(?:[ \t]*[0-9])+\.(?:[ \t]*[0-9])+)|(?:\.(?:[ \t]*[0-9])+)|(?:(?:[ \t]*[0-9])+\.))(?P<exponent>(?:[eE][+-]?(?:[ \t]*[0-9])*)?)"

    t.value = liblex.hDEC(t.value)
    return t

def t_IDENT(t):
    r"(?P<value>[a-zA-Z0-9\$_]+)"

    try:
        t.value = liblex.hIDENT(t.value)
    except NameError:
        t.type = t.value.upper()

    return t

def t_PROCBLOCK(t):
    r"\#![a-zA-Z]+(\s[^\n\{\}]*)?\{" r"(.|\n)*?" r"\#![ \t]*\}"

    t.value = liblex.hPROCBLOCK(t.value)
    return t

def t_PROCDIR(t):
    r"\#![a-zA-Z0-9]+(\s.*)?"
    t.value = liblex.hPROCDIR(t.value)
    return t

def t_COMMENT(t):
    r"\#.*"
    return

def t_NEWLINE(t):
    r"([\n;]\s*)+"
    t.lexer.lineno += t.value.count("\n")

    if not hasattr(t.lexer, "subcol"):
        t.lexer.subcol = {}

    t.lexer.subcol[t.lexer.lineno] = t.lexpos

    return t

def t_error(t):
    pass

# Deal with reserved words
reserved = {}
for i in ("mod", "and", "or", "not", "in", "is", "catch", "class", "else", "elif", "finally", "for", "fn", "yield", "if", "return", "throw", "try", "while", "with", "del", "extern", "import", "break", "continue", "as", "assert"):
    reserved[i] = i.upper()
tokens += reserved.values()

literals = "%()[]{}@,:.`#?+-*/^|<>!"

t_PLUSPLUS = r"\+\+"
t_MINUSMINUS = r"\-\-"
t_SLASHSLASH = r"\/\/"
t_DOTDOTDOT = r"\.\.\."
t_EQOP = r"(?<![<>])(\+|\-|\^|\/|\/\/|\*|<<|>>)\=(?![=<>])"
t_ASSIGN = r"(?<![<>])\=(?![=<>])"
# The look[behind|ahead] is needed so that LE and GE match correctly
t_LTLT = r"\<\<"
t_GTGT = r"\>\>"
t_LE = r"\<\=|\=\<"
t_GE = r"\>\=|\=\>"
t_NE = r"\!\="
t_EQ = r"\=\="

t_ignore = " \t\f\v\r"

import objects.about
_p = objects.about.mainpath
if not _p.endswith("core/"):
    _p += "core/"

# Stupid workaround
import sys
__ = sys.stderr
class Dummy:
    write = lambda x: None
sys.stderr = Dummy
lex.lex(outputdir=_p[:-6]+"/build", optimize=1)
sys.stderr = __

def parse(s):
    lex.lexer.lineno = 0
    lex.input(s)
    global in_put
    in_put = s

    return list(iter(lex.token, None))

def isdone(s):
    try:
        l = parse(s)
    except lex.LexError:
        return True

    count = [0, 0, 0]
    for i in l:
        if i.value == "{": count[2] += 1
        elif i.value == "}": count[2] -= 1
        elif i.value == "[": count[1] += 1
        elif i.value == "]": count[1] -= 1
        elif i.value == "(": count[0] += 1
        elif i.value == ")": count[0] -= 1

    # Need better way to do this...
    return all(i <= 0 for i in count) \
        or re.search("\#![a-zA-Z0-9 \t]*\{(.|\n)*", s) \
        and not re.search("\#![a-zA-Z0-9 \t]*\{(.|\n)*\#![ \t]*\}", s)

def _test(f):
    if not f:
        try:
            while True:
                lex.input(raw_input("lex> ").replace("!\\n", "\n") + "\n")
                for tok in iter(lex.token, None):
                    if len(tok.type) == 1:
                        print "'" + tok.type + "'",
                    else:
                        print "|" + tok.type + ((": " + repr(tok.value)) if type(tok.value) != type("") else "") + "|",
                print
        except (KeyboardInterrupt, EOFError):
            print
    else:
        lex.input(open(f).read())
        for tok in iter(lex.token, None):
            if len(tok.type) == 1:
                print "'" + tok.type + "'",
            else:
                print "|" + tok.type + ": " + repr(tok.value) + "|",
        print

if __name__ == "__main__":
    _test()
