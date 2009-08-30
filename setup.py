#!/usr/bin/env python

from distutils.core import setup
import distcommands.html, distcommands.test, distcommands.clean

# Generate lex and parse tables
import oranj.core.parser

setup(
    name="oranj",
    version="0.6",
    description="Oranj Programming Language",
    author="Pavel Panchekha",
    author_email="pavpanchekha@gmail.com",
    url="http://panchekha.no-ip.com:8080/pavpan/oranj/",
    packages=["oranj", "oranj.core", "oranj.pystdlib", "oranj.core.objects", "oranj.support"],
    package_dir={"oranj.core": "oranj/core", "oranj": "oranj"},
    package_data={"oranj.core": ["lib/errorcontext.py", "lib/odict.py", "lib/files.py", "lib/terminal.py", "lib/ply/lex.py", "lib/ply/yacc.py", "lib/ply/__init__.py"], "oranj": ["build/parsetab.py", "build/lextab.py", "stdlib/*", "sitelib/*"]},
    scripts=["scripts/oranj"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Interpreters",
    ],
    long_description = """\
A pythonic, dynamic programming language
----------------------------------------

A new dynamic, interpreted programming language, with
a focus on GUI and web development. It makes programming
enjoyable and easy, and makes enabling advanced features
direct and fast.
""",
    requires=["ply"],
    cmdclass = {
        "html": distcommands.html.MakeDoc,
        "test": distcommands.test.RunTests,
        "clean": distcommands.clean.Clean,
    }
)
