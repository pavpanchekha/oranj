import os
import sys

if "-h" in sys.argv:
    print "USAGE: python mkdoc.py [-s] [-o outdir]"
    print "    -s  Silent mode"
    print "    -o  Output directory. Relative or absolute"
    sys.exit()

import codecs
from collections import namedtuple

try:
    from genshi.template import TemplateLoader
except ImportError:
    print "Genshi is required to build the documentation"
    print "Please install Genshi and rerun this script"
    sys.exit(1)

loader = TemplateLoader(
    os.path.join(os.path.dirname(__file__), "resources", "templates"),
    auto_reload=True
)

Doc = namedtuple("Doc", ["title", "sections"])
Section = namedtuple("Section", ["title", "blocks"])
Block = namedtuple("Block", ["type", "content"])

def render_block(block):
    if block.type == "p":
        return u"        <p>%s</p>\n" % block.content.replace("\n", " ")
    elif block.type in ("oranj", "python", "cpp", "sh"):
        content = block.content
        content = content.replace("&", "&amp;")
        content = content.replace("<", "&lt;")
        content = content.replace(">", "&gt;")
        return u"        <pre class='sh_%s'>%s</pre>\n" % (block.type, content)
    elif block.type == "comment":
        return u"        <!-- %s -->\n" % block.content.replace("\n", " ")
    elif block.type == "heading":
        return u"        <h3>%s</h3>\n" % block.content.strip() 

def parse(stream):
    prevline = ""
    buffer = []
    ctype = "p"
    
    title = ""
    sections = []
    sectitle = ""
    blocks = []
    
    for l in stream:
        if l.strip("=") == "\n" and len(l) >= len(prevline) >= 4 and not title:
            title = prevline.strip()
            buffer = []
        elif l.strip("-") == "\n" and len(l) >= len(prevline) >= 4:
            buffer = []
            if sectitle:
                sections.append(Section(sectitle, blocks))
                blocks = []
                
            sectitle = prevline.strip()
        elif l == "::oranj::\n":
            if buffer: blocks.append(Block(ctype, "".join(buffer)))
            buffer = []
            ctype = "oranj"
        elif l == "::python::\n":
            if buffer: blocks.append(Block(ctype, "".join(buffer)))
            buffer = []
            ctype = "python"
        elif l == "::cpp::\n":
            if buffer: blocks.append(Block(ctype, "".join(buffer)))
            buffer = []
            ctype = "cpp"
        elif l == "::sh::\n":
            if buffer: blocks.append(Block(ctype, "".join(buffer)))
            buffer = []
            ctype = "sh"
        elif l == "::comment::\n":
            if buffer: blocks.append(Block(ctype, "".join(buffer)))
            buffer = []
            ctype = "comment"
        elif l == "::heading::\n":
            if buffer: blocks.append(Block(ctype, "".join(buffer)))
            buffer = []
            ctype = "heading"
        elif l == "\n":
            if buffer: blocks.append(Block(ctype, "".join(buffer)))
            buffer = []
            ctype = "p"
        else:
            buffer.append(l)

        prevline = l

    if buffer: blocks.append(Block(ctype, "".join(buffer)))
    if blocks: sections.append(Section(sectitle, blocks))
    
    return Doc(title, sections)

if "-o" in sys.argv:
    if sys.argv[-1] == "-o":
        print "Error: No output directory specified"
        sys.exit(1)
    else:
        outdir = sys.argv[sys.argv.index("-o") + 1]
else:
    outdir = "./"

for root, dirs, files in os.walk("."):
    if "resources" in dirs:
        dirs.remove("resources")

    for dir in dirs:
        if not os.path.exists(os.path.join(outdir, root)):
            os.mkdir(os.path.join(outdir, root))
    
    for obj in [os.path.join(root, obj) for obj in files if obj.endswith(".doc")]:
        if "-s" not in sys.argv:
            print obj, "->", os.path.join(outdir, obj[:-4] + ".html")
    
            doc = parse(codecs.open(obj, "r", "utf-8"))
            
            outfile = open(os.path.join(outdir, obj[:-4] + ".html"), "w")
            outfile.write(loader.load("main.html").generate(title=doc.title, sections=doc.sections, render=render_block).render("html", doctype="html"))
            outfile.close()

if not os.path.samefile(".", outdir):
    import shutil
    shutil.rmtree(os.path.join(outdir, "resources"))
    shutil.copytree(os.path.join(".", "resources"), os.path.join(outdir, "resources"))
