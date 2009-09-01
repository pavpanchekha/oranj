from distutils.cmd import Command
from distutils.errors import *

import codecs
from collections import namedtuple
import os, sys

class DocParser:
    # I actually don't know why this is in a class; it should certainly
    # be at some point rewritten so that it actually, you know, uses that
    # fact. Ugh. This looks like JAVA.
    
    Doc = namedtuple("Doc", ["title", "sections"])
    Section = namedtuple("Section", ["title", "blocks"])
    Block = namedtuple("Block", ["type", "content"])
    # These should be as light-weight as possible
    
    codeblocks = ["oranj", "python", "cpp", "sh"]
    blocks = ["heading", "comment"] + codeblocks
    
    blocks_compiled = ["::" + name + "::\n" for name in blocks]
    
    @classmethod
    def render_block(cls, block):
        if block.type == "p":
            return u"        <p>%s</p>\n" % block.content.replace("\n", " ")
        elif block.type in cls.codeblocks:
            content = block.content
            content = content.replace("&", "&amp;")
            content = content.replace("<", "&lt;")
            content = content.replace(">", "&gt;")
            return u"        <pre class='sh_%s'>%s</pre>\n" % (block.type, content)
        elif block.type == "comment":
            return u"        <!-- %s -->\n" % block.content.replace("\n", " ")
        elif block.type == "heading":
            return u"        <h3>%s</h3>\n" % block.content.strip()
    
    @classmethod
    def parse(cls, stream):
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
                    sections.append(cls.Section(sectitle, blocks))
                    blocks = []
                    
                sectitle = prevline.strip()
            elif l in cls.blocks_compiled:
                if buffer: blocks.append(cls.Block(ctype, "".join(buffer)))
                buffer = []
                ctype = l[2:-3]
            elif l == "\n":
                if buffer: blocks.append(cls.Block(ctype, "".join(buffer)))
                buffer = []
                ctype = "p"
            else:
                buffer.append(l)
    
            prevline = l
    
        if buffer: blocks.append(cls.Block(ctype, "".join(buffer)))
        if blocks: sections.append(cls.Section(sectitle, blocks))
        
        return cls.Doc(title, sections)
    
    @classmethod
    def mkdoc(cls, indir, silent=False, outdir="."):
        loader = TemplateLoader(
            os.path.join(indir, "resources", "templates"),
            auto_reload=True
        )
        
        for root, dirs, files in os.walk(indir):
            if "resources" in dirs:
                dirs.remove("resources")
        
            for dir in dirs:
                if not os.path.exists(os.path.join(outdir, root)):
                    os.mkdir(os.path.join(outdir, root))
            
            for obj in [os.path.join(root, obj) for obj in files if obj.endswith(".doc")]:
                if "-s" not in sys.argv:
                    print obj, "->", os.path.join(outdir, os.path.basename(obj[:-4] + ".html"))
            
                doc = cls.parse(codecs.open(obj, "r", "utf-8"))
                
                outfile = open(os.path.join(outdir, os.path.basename(obj[:-4] + ".html")), "w")
                outfile.write(loader.load("main.html").generate(title=doc.title, sections=doc.sections, render=cls.render_block).render("html", doctype="html"))
                outfile.close()
        
        if not os.path.samefile(indir, outdir):
            import shutil
            shutil.rmtree(os.path.join(outdir, "resources"))
            shutil.copytree(os.path.join(indir, "resources"), os.path.join(outdir, "resources"))

class MakeDoc(Command):
    description = "Generate documentation; make HTML files"
    user_options = [
        ("outdir=", "o", "Output directory for HTML files. Resrouces will also be copied there"),
        ("silent", "s", "Whether to report what's happening")]
    
    def initialize_options(self):
        self.indir = os.path.join(os.getcwd(), "doc")
        self.outdir = self.indir
        self.silent = False
    
    def finalize_options(self):
        self.outdir = os.path.abspath(os.path.expanduser(self.outdir))
        print self.outdir
    
    def run(self):
        global TemplateLoader
        try:
            from genshi.template import TemplateLoader
        except ImportError:
            print "Genshi is required to build the documentation"
            print "Please install Genshi and rerun this script"
            sys.exit(1)
        
        DocParser.mkdoc(self.indir, self.silent, self.outdir)


if __name__ == "__main__":
    import sys
    if "-h" in sys.argv:
      print "USAGE: python html.py [-s] [-o outdir]"
      print "Converts all the docs in the current directory to html files."
      print "    -s  Silent mode"
      print "    -o  Output directory. Relative or absolute"
      sys.exit()
    
    try:
        from genshi.template import TemplateLoader
    except ImportError:
        print "Genshi is required to build the documentation"
        print "Please install Genshi and rerun this script"
        sys.exit(1)
    
    if "-o" in sys.argv:
        if sys.argv[-1] == "-o":
            print "Error: No output directory specified"
            sys.exit(1)
        else:
            outdir = sys.argv[sys.argv.index("-o") + 1]
    else:
        outdir = "./"
    
    if "-s" not in sys.argv:
        silent = False
    else:
        silent = True
    
    DocParser.mkdoc(".", silent, outdir)
