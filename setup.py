#!/usr/bin/env python

# Linux only, tested on Ubuntu, nothing else
# TODO: Add Windows, (mac?) support

from distutils.core import setup
import distcommands.test, distcommands.clean
import distcommands.profile
import sphinx.setup_command

# Generate lex and parse tables
import oranj.core.parser

from distutils.command.install_data import install_data
class post_install(install_data):
    def run(self):
        # Call parent 
        install_data.run(self)
        # Execute commands
        import subprocess
        import sys
        
        subprocess.call(["update-mime-database", "/usr/local/share/mime/"])
        subprocess.call(["gtk-update-icon-cache", "/usr/share/icons/hicolor"])
        mimetypes = open("/etc/mime.types", "a")
        mimetypes.write("text/x-oranj\t\t\tor")
        mimetypes.close()

setup(
name="oranj",
version="0.7",
description="Oranj Programming Language",
author="Pavel Panchekha",
author_email="pavpanchekha@gmail.com",
url="http://panchekha.no-ip.com:8080/pavpan/oranj/",

packages=["oranj", "oranj.core", "oranj.pystdlib", "oranj.core.objects", "oranj.support"],
package_dir={"oranj.core": "oranj/core", "oranj": "oranj"},
package_data={"oranj.core": ["lib/errorcontext.py", "lib/odict.py", "lib/files.py", "lib/terminal.py", "lib/ply/lex.py", "lib/ply/yacc.py", "lib/ply/__init__.py"], "oranj": ["build/parsetab.py", "build/lextab.py", "stdlib/*", "sitelib/*"]},

scripts=["scripts/oranj"],
data_files=[
    ("/usr/local/share/mime/packages", ["system/x-oranj.xml"]),
    ("/usr/share/icons/hicolor/scalable/apps", ["system/icons/apps/oranj.svg"]),
    ("/usr/share/icons/hicolor/scalable/mimetypes", ["system/icons/mimetypes/text-x-oranj.svg"]),
],

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
    "html": sphinx.setup_command.BuildDoc,
    "test": distcommands.test.RunTests,
    "clean": distcommands.clean.Clean,
    "profile": distcommands.profile.Profile,
    "install_data": post_install,
}
)
