#!/usr/bin/env python

import ply.lex as lex
import re
import sys

tokens = [
    "STRING", "DEC", "INT", "BOOL", "NIL", "IDENT", "PLUSPLUS", "MINUSMINUS",
    "SLASHSLASH", "GE", "LE", "NE", "EQ", "LTLT", "GTGT", "DOTDOTDOT", "EQOP",
    "NEWLINE", "PROCDIR"
]

# PUNCTUATION is never used

def t_BOOL(t):
    r"true|false"

    t.value = ("BOOL", t.value == "true")
    return t

def t_NIL(t):
    r"nil"

    t.value = None
    return t

def t_STRING(t):
    r"""[a-z]*((['"])(?:\3\3)?)(?:\\\2|[^\2])*?\2"""

    i = 0
    while t.value[i].isspace(): i += 1
    prefix = t.value[:i]
    data = t.value[i:].strip("\"\'")
    t.value = ("STRING", data, prefix)

    return t # TODO: Implement String class

def t_INT(t):
    r"""(?<![\.eE]|\d)(?:0(?:\w))?(?:(?:\s*[0-9])+)(?!\s*\.|\d)"""

    if t.value[0] == 0:
        try:
            base = {
                "d": 10,
                "b": 2,
                "h": 16,
                "a": 36,
                "o": 8,
                "s": 17,
                }[t[1]]
        except:
            base = 10
            print "Error (line %d): Illegal base %s" % (t.lexer.lineno, t[1])

        t.value = t.value[2:]
    else:
        base = 10

    t.value = ("INT", t.value.replace(" ", ""), base)
    return t # TODO: Implement Integer class

def t_DEC(t):
    r"(?P<number>(?:(?:\s*[0-9])+\.(?:\s*[0-9])+)|(?:\.(?:\s*[0-9])+)|(?:(?:\s*[0-9])+\.))(?P<exponent>(?:[eE][+-]?(?:\s*[0-9])*)?)"

    t.value = t.value.lower()
    if "e" in t.value:
        exp = int(t.value[t.value.find("e")+1:].replace(" ", ""))
        t.value = t.value[:t.value.find("e")]
    else:
        exp = 0

    t.value = ("DEC", t.value.replace(" ", "") + "E" + str(exp))
    return t # TODO: Implement Decimal class

def t_IDENT(t):
    r"(?:^|\b)(?P<value>[a-zA-Z0-9$_]+)(?:\b|$)"

    t.type = reserved.get(t.value, 'IDENT') # Taken from http://github.com/alex/alex-s-language/
    return t

t_ignore = " \t\f\v\r"

def t_NEWLINE(t):
    r"([\n;]\s*)+"
    t.lexer.lineno += t.value.count("\n")
    return t

def t_PROCDIR(t):
    r"\#![a-zA-Z0-9]*"
    return t

def t_COMMENT(t):
    r"\#.*"
    return

def t_error(t):
    print "Error (line %d): Illegal character `%s`" % (t.lexer.lineno, t.value)
    t.lexer.skip(1)

# Deal with reserved words
reserved = {}
for i in ("mod", "and", "or", "not", "in", "is", "catch", "class", "else", "elif", "finally", "for", "fn", "yield", "if", "return", "throw", "try", "while", "with", "del", "extern", "import", "break", "continue", "as", "assert", "inf"):
    reserved[i] = i.upper()
tokens += reserved.values()

literals = "%()[]{}@,:.`;#?+-*/^|<>"

t_PLUSPLUS = r"\+\+"
t_MINUSMINUS = r"\-\-"
t_SLASHSLASH = r"\/\/"
t_DOTDOTDOT = r"\.\.\."
t_EQOP = r"(\+|\-|\^|\/|\/\/|\*|<<|>>)?\=(?!\=)"
t_LTLT = r"\<\<"
t_GTGT = r"\>\>"
t_LE = r"\<\="
t_GE = r"\>\=|\=\>"
t_NE = r"\!\="
t_EQ = r"\=\="

lex.lex()

def parse(s):
    lex.input(s)
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
                lex.input(raw_input("lex> ") + "\n")
                for tok in iter(lex.token, None):
                    if len(tok.type) == 1:
                        print "'" + tok.type + "'",
                    else:
                        print "|" + tok.type + "|",
                print
            except (KeyboardInterrupt, EOFError):
                print
                break
