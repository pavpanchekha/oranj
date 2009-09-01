from objects.orobject import OrObject
from collections import namedtuple
from libbuiltin import typeof
from objects.number import Number
import objects.constants as constants
import sys

overrides = {
    "stdin": "", # oranj script -
    "count": "q", # in `who`
    "digits": "n", # csplit
    "exit": "x",
    "extract": "x",
    "zip": "z",
    "gzip": "z",
    "compress": "z",
    "literal": "N", # ls
}

class CLIArgs:
    def __init__(self):
        self.mandatory = []
        self.short = {}
        self.long = {}
        self.dump = None
        self.kwdump = None

def shortarg(arg):
    return [arg[0], arg[0].swapcase] + (overrides[arg] if arg in overrides else [])

def getargs(intp, arglist):
    args = CLIArgs()
    
    for i in arglist:
        if i[0] == "ARG":
            args.mandatory.append(i[1])
            args.long[i[1]] = "str"
            for short in shortarg(i[1]):
                if short not in args.short:
                    args.short[short] = i[1]
                    break
        elif i[0] == "DEFARG":
            args.long[i[1]] = typeof(intp.run(i[2]))
            for short in shortarg(i[1]):
                if short not in args.short:
                    args.short[short] = i[1]
                    break
        elif i[0] == "UNWRAPABLE":
            args.mandatory.append(i[1])
            if not args.dump:
                args.dump = i[1]
        elif i[0] == "UNWRAPABLEKW":
            if not args.kwdump:
                args.kwdump = i[1]
    
    return args

def evalval(type, val):
    if type == "int":
        return Number(val, intonlystr=True)
    elif type == "num":
        return Number(val)
    elif type == "list":
        return OrObject.from_py(val.split(","))
    elif type == "bool":
        return constants.true
    elif type == "str":
        return OrObject.from_py(val)
    else:
        raise TypeError, "`%s` type not supported for command-line \
arguments" % type

def parseargs(args, schema):
    passargs = {}
    takingopts = True
    errors = False
    setval = ""
    
    if schema.dump:
        passargs[schema.dump] = [] # Not OrObjected yet
    if schema.kwdump:
        passargs[schema.kwdump] = {} # Also not OO'd yet
    
    for i in args:
        if i.startswith("--") and len(i) > 2 and takingopts:
            kw, t, val = i[2:].partition("=")
            
            if kw not in schema.long and not schema.kwdump:
                print "ERROR: Unknown option `%s`" % kw
                errors = True
                continue
            elif schema.kwdump:
                passargs[schema.kwdump][kw] = evalval("str", val)
                continue
            
            if kw in schema.mandatory:
                schema.mandatory.remove(kw)
            
            passargs[kw] = evalval(schema.long[kw], val)
        elif i == "--" and takingopts:
            takingopts = False
        elif i.startswith("-") and takingopts:
            key = i[1:2]
            val = i[2:]
            
            if key not in schema.short:
                print "ERROR: Unknown option `%s`" % key
                errors = True
                continue
            elif schema.kwdump:
                setval = ":kwdump:"
                continue
            
            if schema.short[key] in schema.mandatory:
                schema.mandatory.remove(schema.short[key])
            
            if schema.long[schema.short[key]] == "bool":
                passargs[schema.short[key]] = constants.true
            elif val:
                passargs[schema.short[key]] = evalval(schema.long[schema.short[key]], val)
            else:
                setval = schema.short[key]
        elif setval:
            if setval == ":kwdump:":
                passargs[schema.kwdump][setval] = evalval("str", val)
            else:
                passargs[setval] = evalval(schema.long[setval], i)
                setval = ""
        else:
            try:
                kw = schema.mandatory[0]
            except IndexError:
                print "ERROR: Too many arguments"
                errors = True
                continue
            
            if kw == schema.dump:
                passargs[schema.dump].append(i)
                takingopts = False
                continue
            
            passargs[kw] = evalval(schema.long[kw], kw)
            schema.mandatory.pop(0)
    
    if schema.dump:
        passargs[schema.dump] = OrObject.from_py(passargs[schema.dump])
    if schema.kwdump:
        passargs[schema.kwdump] = OrObject.from_py(passargs[schema.kwdump])
    
    if len(schema.mandatory) and schema.mandatory[0] != schema.dump:
        m = len(schema.mandatory) - (1 if schema.dump in schema.mandatory else 0)
        print "ERROR: Missing %d arguments; consult --help for command sytnax" % m
        errors = True
    if setval:
        print "ERROR: Expecting value for argument `%s`" % setval
        errors = True
    
    if errors:
        sys.exit(1)
    
    return passargs

def run_main(intp, args):
    if "--help" in args or "-h" in args or "-?" in args \
            and "$$help" in intp.curr:
        __help = intp.curr["$$help"]
        if typeof(__help) == "str":
            print __help
        else:
            __help()
    elif "--version" in args and "$$version" in intp.curr:
        __version = intp.curr["$$version"]
        if typeof(__version) == "str":
            print __version
        else:
            __version()
    else:
        main = intp.curr["$$main"]
        schema = getargs(intp, main.arglist)
        kwargs = parseargs(args, schema)
        main(**kwargs)

def run(intp, args):
    if "$$main" in intp.curr:
        run_main(intp, args)
    return