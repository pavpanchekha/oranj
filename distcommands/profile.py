#!/usr/bin/env python

from distutils.cmd import Command
from distutils.errors import *

import os
import tempfile

class Profile(Command):
    description = "Profile the application running common examples"
    user_options = [("files=", "f", "File to run"),]
    
    def initialize_options(self):
        self.files = "primes.or"
    
    def finalize_options(self):
        self.files = map(lambda x: os.path.join(os.getcwd(), "examples", x), self.files.split(","))
    
    def run(self):
        try:
            import cProfile as profile
        except ImportError:
            print "WARNING: Using profile instead of cProfile. Timings will be way off"
            import profile
        
        import oranj.core.oranj
        import oranj.core.interpreter
        base_i = oranj.core.interpreter.Interpreter()
        
        for i in self.files:
            xxx, t = tempfile.mkstemp()
            try:
                profile.runctx("oranj.core.oranj.run_file(base_i, i)",
                               {"i": [i], "base_i": base_i, "oranj": oranj}, {}, t)
            except Exception:
                import traceback
                traceback.print_exc()
                import sys
                sys.exit(1)
            import pstats
            p = pstats.Stats(t)
            p.strip_dirs()
            p.sort_stats("calls", "time")
            print "============== %s ==============" % i
            p.print_stats(10)
            os.remove(t)