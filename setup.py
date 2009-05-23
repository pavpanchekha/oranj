#!/usr/bin/env python

from distutils.core import setup

setup(name="Oranj",
      version="0.5",
      description="Oranj Programming Language",
      author="Pavel Panchekha",
      author_email="pavpanchekha@gmail.com",
      url="http://panchekha.no-ip.com:8080/pavpan/oranj/",
      packages=["oranj", "oranj.core", "oranj.pystdlib", "oranj.core.objects"],
      package_dir={"oranj.core": "oranj/core", "oranj": "oranj"},
      package_data={"oranj.core": ["lib/errorcontext.py", "lib/odict.py", "lib/files.py", "lib/terminal.py", "lib/ply/lex.py", "lib/ply/yacc.py"], "oranj": ["build/parsetab.py"]},
      scripts=["scripts/oranj"],
#      requires=["ply (>=3.1)", "files (>=1.0)"],
      )
