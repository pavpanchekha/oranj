
# Some processing directives make too much sense in the core interpreter file
# (such as debug)
# So only extras should be placed here

def drop(args, i, glob={}):
    i.level += 1
    print "Dropping to oranj shell. Use C-d or #!undrop to undrop"
    glob["Interpreter"].run_console(i)
    i.level -= 1

def undrop(args, i, glob={}):
    raise glob["DropI"]

def clear(args, i, glob={}):
    import libintp
    libintp.clear_screen()

def exit(args, i, glob={}):
    import sys
    sys.exit()

def pydrop(args, i, glob={}):
    raise glob["PyDropI"]

def pyerror(args, i, glob={}):
    import traceback
    traceback.print_exc()

dirs = {"drop": drop, "undrop": undrop, "clear": clear, "exit": exit, "pydrop": pydrop, "pyerror": pyerror}

def python(args, body, i, glob={}):
    glob["intp"] = i
    exec body in glob

def output(args, body, i, glob={}):
    i.curr["io"].write(body)

def nil(args, body, i, glob={}):
    return

def xml(args, body, i, glob={}):
    try:
        import elementtree
    except ImportError:
        import xml.etree.ElementTree as elementtree
        
    return elementtree.fromstring(body)

blocks = {"python": python, "output": output, "nil": nil, "xml": xml}
