#!/usr/bin/env python

import ply.lex as lex
import re
import sys

tokens = [
    "STRING", "DEC", "INT", "BOOL", "NIL", "IDENT", "PLUSPLUS", "MINUSMINUS",
    "SLASHSLASH", "GE", "LE", "NE", "EQ", "LTLT", "GTGT", "DOTDOTDOT", "EQOP",
    "NEWLINE", "PROCDIR", "PROCBLOCK", "INF"
]

# WARNING: t_STRING ***must*** be first in the list of functions.
# Because otherwise \n will refer to something else.
# Oh, and add one to whatever subgroup you think you refer to.

def t_STRING(t):
    r"""[a-z]*((['"])(?:\3\3)?)(?:\\\3|[^\2])*?\2"""

    i = 0
    while t.value[i].isspace(): i += 1
    prefix = t.value[:i]
    data = t.value[i:].strip("\"\'")
    t.value = ("STRING", data, prefix)

    return t # TODO: Implement String class

def t_BOOL(t):
    r"true|false"

    t.value = ("BOOL", t.value == "true")
    return t

def t_NIL(t):
    r"nil"

    t.value = ("NIL")
    return t

def t_INF(t):
    r"inf"
    
    if t.value[0] in "+-":
        t.value = ("INF", t.value[0])
    else:
        t.value = ("INF", "+")
    
    return t

def t_INT2(t):
    r"""(?<![\.eE]|\d)(?:(?:[ \t]*[0-9])+)(?![ \t]*\.|\d|\w)"""

    t.value = ("INT", t.value.replace(" ", ""), 10)
    t.type = "INT"
    return t

def t_INT(t):
    r"""(?<![\.eE]|\d)(?:0(?:\w))(?:(?:[ \t]*[0-9a-zA-Z])+)(?![ \t]*\.|\d|\w)"""

    if t.value[0] == "0":
        try:
            base = {
                "d": 10,
                "b": 2,
                "h": 16,
                "a": 36,
                "o": 8,
                "s": 17,
                }[t.value[1]]
        except:
            base = 10
            print "Error (line %d): Illegal base %s" % (t.lexer.lineno, t.value[1])

        t.value = t.value[2:]
    else:
        base = 10

    t.value = ("INT", t.value.replace(" ", ""), base)
    return t # TODO: Implement Integer class

def t_DEC(t):
    r"(?P<number>(?:(?:[ \t]*[0-9])+\.(?:[ \t]*[0-9])+)|(?:\.(?:[ \t]*[0-9])+)|(?:(?:[ \t]*[0-9])+\.))(?P<exponent>(?:[eE][+-]?(?:[ \t]*[0-9])*)?)"

    t.value = t.value.lower()
    if "e" in t.value:
        exp = int(t.value[t.value.find("e")+1:].replace(" ", ""))
        t.value = t.value[:t.value.find("e")]
    else:
        exp = 0

    t.value = ("DEC", t.value.replace(" ", "") + "E" + str(exp))
    return t # TODO: Implement Decimal class

def t_IDENT(t):
    r"(?P<value>[a-zA-Z0-9\$_]+)"

    t.type = reserved.get(t.value, 'IDENT') # Taken from http://github.com/alex/alex-s-language/
    if t.value == "inf":
        t.value = ("INF", "+")
    return t

t_ignore = " \t\f\v\r"

def t_NEWLINE(t):
    r"([\n;]\s*)+"
    t.lexer.lineno += t.value.count("\n")

    if not hasattr(t.lexer, "subcol"):
        t.lexer.subcol = {}

    t.lexer.subcol[t.lexer.lineno] = t.lexpos
    
    return t

def t_PROCDIR(t):
    r"\#![a-zA-Z0-9 \t]+\n"
    t.value = ["PROCDIR"] + t.value[2:].split()
    return t

def process_body(s):
    if s and s[0] == "\n":
        s = s[1:]
        
    if "\n" in s:
        t = s[:s.find("\n")]
        ws = t[:t.find(t.strip())]
        
        s = s.split("\n")
        for i, v in enumerate(s):
            if v.startswith(ws):
                s[i] = v[len(ws):]
        s = "\n".join(s)

    return s

def t_PROCBLOCK(t):
    r"\#![a-zA-Z0-9 \t]*\{" r"(.|\n)*" r"\#![ \t]*\}"

    txt = t.value
    pstart = txt.find("{")
    pend = txt.rfind("#!", 2)
    
    header = txt[2:pstart].strip()
    body = txt[pstart+1:pend]

    t.value = ["PROCBLOCK", header.split(), process_body(body)]
    return t

def t_COMMENT(t):
    r"\#.*"
    return

def t_error(t):
    print "Error (line %d): Illegal character `%s`" % (t.lexer.lineno, repr(t.value)[1:-1])

# Deal with reserved words
reserved = {}
for i in ("mod", "and", "or", "not", "in", "is", "catch", "class", "else", "elif", "finally", "for", "fn", "yield", "if", "return", "throw", "try", "while", "with", "del", "extern", "import", "break", "continue", "as", "assert"):
    reserved[i] = i.upper()
tokens += reserved.values()

literals = "%()[]{}@,:.`;#?+-*/^|<>"

t_PLUSPLUS = r"\+\+"
t_MINUSMINUS = r"\-\-"
t_SLASHSLASH = r"\/\/"
t_DOTDOTDOT = r"\.\.\."
t_EQOP = r"(?<![<>])(\+|\-|\^|\/|\/\/|\*|<<|>>)?\=(?!\=)(?![<>])"
# The look[behind|ahead] is needed so that LE and GE match correctly
t_LTLT = r"\<\<"
t_GTGT = r"\>\>"
t_LE = r"\<\=|\=\<"
t_GE = r"\>\=|\=\>"
t_NE = r"\!\="
t_EQ = r"\=\="

lex.lex()

def parse(s):
    lex.input(s)
    global in_put
    in_put = s
    
    return list(iter(lex.token, None))

def isdone(s):
    l = parse(s)
    
    count = [0, 0, 0]
    for i in l:
        if i.value == "{": count[2] += 1
        elif i.value == "}": count[2] -= 1
        elif i.value == "[": count[1] += 1
        elif i.value == "]": count[1] -= 1
        elif i.value == "(": count[0] += 1
        elif i.value == ")": count[0] -= 1
    return all(i <= 0 for i in count)

if __name__ == "__main__":
    if "-t" in sys.argv:
        # Test code
        pass
    else:
        while True:
            try:
                lex.input(raw_input("lex> ").replace("!\\n", "\n") + "\n")
                for tok in iter(lex.token, None):
                    if len(tok.type) == 1:
                        print "'" + tok.type + "'",
                    else:
                        print "|" + tok.type + "|",
                print
            except (KeyboardInterrupt, EOFError):
                print
                break
