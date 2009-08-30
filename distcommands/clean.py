from distutils.cmd import Command
from distutils.errors import *

import os

class Clean(Command):
    user_options = []

    def initialize_options(self):
        self._clean_me = []
        for root, dirs, files in os.walk('.'):
            for dir in ("lib", "build", "dist", "bin", "include"):
                if root == "." and dir in dirs:
                    dirs.remove(dir)
            
            for f in files:
                if f.endswith('.pyc'):
                    self._clean_me.append(os.path.join(root, f))
        
        for f in [x for x in os.listdir("doc") if x.endswith(".html")]:
            self._clean_me.append(f)
        
        for f in os.listdir("oranj/build"):
            self._clean_me.append(f)

    def finalize_options(self):
        pass

    def run(self):
        for clean_me in self._clean_me:
            try:
                os.unlink(clean_me)
            except:
                pass