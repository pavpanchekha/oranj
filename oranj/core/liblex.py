# -*- coding: utf-8 -*-

bases = {"d": 10, "b": 2, "h": 16, "a": 36, "o": 8, "s": 17}
reserved = ["mod", "and", "or", "not", "in", "is", "catch", "class", "else", \
    "elif", "finally", "for", "fn", "yield", "if", "return", "throw", "try", \
    "while", "with", "del", "extern", "import", "break", "continue", "as", \
    "assert"]

def hSTRING(t):
    i = 0

    while t[i] not in "\'\"": i += 1

    prefix = t[:i]
    data = t[i:]
    if data.startswith("\"\"\"") and data.endswith("\"\"\""):
        data = data[3:-3]
    elif data.startswith("\"") and data.endswith("\""):
        data = data[1:-1]
    elif data.startswith("\'\'\'") and data.endswith("\'\'\'"):
        data = data[3:-3]
    elif data.startswith("\'") and data.endswith("\'"):
        data = data[1:-1]

    return ("STRING", data, prefix)

def hBOOL(t):
    return ("BOOL", t == "true")

def hNIL(t):
    return ("NIL",)

def hINF(t):
    return ("INF",)

def hINT(t):
    t = t.replace(" ", "")

    if t[0] == "0" and len(t) > 1:
        if t[1] not in bases:
            raise SyntaxError("Invalid base for integers")
        else:
            return ("INT", t[2:], bases[t[1]])
    else:
        return ("INT", t.replace(" ", ""), 10)

def hDEC(t):
    t = t.lower()

    if "e" in t:
        exp = int(t[t.find("e")+1:].replace(" ", ""))
        t = t[:t.find("e")]
    else:
        exp = 0

    return ("DEC", t.replace(" ", "") + "E" + str(exp))

def hIDENT(t):
    if t in reserved:
        raise NameError(t + " is a reserved word in oranj")
    else:
        return t

def hPROCDIR(t):
    import shlex
    return ["PROCDIR",  shlex.split(t[2:])]

def __process_procblock(s):
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

def hPROCBLOCK(t):
    import shlex
    pstart = t.find("{")
    pend = t.rfind("#!", 2)

    header = t[2:pstart].strip()
    body = t[pstart+1:pend]

    return ["PROCBLOCK", shlex.split(header), __process_procblock(body)]

