#!/usr/bin/env python

import sys, os
from oranj.core.interpreter import Interpreter
import traceback

class Test(object):
    def __init__(self, tests=None, desc="", tool="python"):
        if not tests: tests = [["", ""]] # Stupid evaluate-once arguments
        self.desc = desc
        self.tests = tests
        self.tool = tool
        
        self.intp = Interpreter()

    def trim(self):
        self.desc = self.desc.strip()
        
        if self.tests[0] == ["", ""]: del self.tests[0]
        
        for i in self.tests:
            i[0] = i[0].strip()
            i[1] = i[1].strip()
            
        self.tool = self.tool.strip()

    def run(self, quiet=False):
        if not self.tests: return 0
        failed = []

        for i in self.tests:
            try:
                out = repr(self.intp.run_code(i[0]))
            except Exception, e:
                failed.append((i[0], i[1], "", traceback.format_exc()))
            else:
                if out != i[1]:
                    failed.append((i[0], i[1], out.strip(), ""))

        if quiet:
            return len(failed)
        
        if not failed:
            print ".", self.desc
            return 0
        else:
            print "F", self.desc, "(" + str(len(failed)) + "/" + str(len(self.tests)) + ")"
            for i in failed:
                print "===== Input: ======"
                print i[0]
                print "===== Expected: ==="
                print i[1]
                if i[2]:
                    print "===== Output: ====="
                    print i[2]
                if i[3]:
                    print "===== Error: ======"
                    print i[3]
                print "==================="
                
            return len(failed)

def parsetests(strtests, deftool="python"):
    tests = []
    curr = Test(tool=deftool)
    
    for s in strtests.split("\n"):
        if len(s) == 0: continue

        if s[0] == "#" and s[1] == "!":
            s = s[2:]
            tests.append(curr)
            curr = Test(tool=s.strip())
        elif s[:2] == "##":
            continue
        elif s[:2] == "# ":
            if curr.tests[-1][0]:
                tests.append(curr)
                curr = Test(desc=s[2:].strip(), tool=curr.tool)
            else:
                curr.desc += "\n" + s[1:].strip()
        elif s[:4] == ">>> ":
            if curr.tests[-1][1]:
                curr.tests.append([s[4:], ""])
            else:
                curr.tests[-1][0] += "\n" + s[4:]
        else:
            curr.tests[-1][1] += "\n" + s

    tests.append(curr)
    
    if tests[0].tests[0] == ["", ""]:
        tests = tests[1:]
    
    return tests

def run(l, quiet=False):
    tot = 0
    failed = 0
    
    for test in l:
        test.trim()
        
        tot += 1
        failed += test.run(quiet)

    if not quiet:
        print "Failed %d out of %d" % (failed, tot)

    return (tot, failed)

def run_file(f, quiet=False, deftool="python"):
    if os.path.isdir(f):
        t = []
        tot = 0
        os.chdir(f)
        for i in [i for i in os.listdir(".") if os.path.isfile(i) and not i.endswith("~") and not i.endswith(".py") and not i.startswith(".")]:
            tt, r = run_file(i, True, deftool)
            tot += tt
            if r > 0:
                t.append((i, r))

        sum = 0
        for i in t:
            sum += i[1]

        print "Failed %d in %d" % (sum, tot)

        if not quiet:
            for i in t:
                print "Failed %d tests in %s" % (i[1], i[0])
        
        return t
    else:
        f = open(f)
        return run(parsetests(f.read(), deftool), quiet)

if __name__ == "__main__":
    args = sys.argv

    if len(args) == 1:
        try:
            run_file(".")
        except (KeyboardInterrupt, EOFError):
            pass
    else:
        if "-t" in args:
            x = args.index("-t")
            if x+1 < len(args):
                tool = args[x + 1]
                del args[x:x + 2]
        else:
            tool = "python"
        
        for i in sys.argv[1:]:
            run_file(i, deftool=tool)
