Easy Command-line Support
=========================

.. index::
    Command-line
    CLI
    Argument Parsing

Basics
------

Yeah. The command line. DOS Box. Black screen with scary white text. That
thing.

oranj, like any good scripting language, allows you to access the command
line for scripts a bit more intense than what a bash script might allow.
Now, one of the annoying parts about writing one of these scripts is
parsing command-line arguments.

oranj does this for you. Suppose, for example, that your script takes a
``--verbose`` option (for added verbosity) and a ``--optimize`` option,
which takes an integer argument (``0`` by default). Here's how to do this
in oranj::

    $$main = fn(verbose=false, optimize=0) {
        # ...
    }

This script can then be called on the command line with the standard syntax:

.. code-block:: sh

    oranj script [-v|--verbose] [-o|--optimize n]

Notice how standard options were generated automatically (shortened forms
included). You can also have mandatory arguments::

    $$main = fn(infile, outfile="") {...}

Here, the ``infile`` paramter is required (and assumed to be a string),
whereas ``outfile`` is not required, is a string argument, and can be
passed with either ``-o file`` or ``--outfile=file``. Of course, if you
want to parse your own arguments, you can easily use ``*args`` arguments::

    $$main = fn(*args) {...}

Note that ``args[0]`` (that is, the script name) is *not* passed to
``args``. There are alternative ways to get at this information; take a
look at the :mod:`oranj` module if you need this (and related) information.

Help and Version Information
----------------------------

A common pattern (and GNU standard) in applications is to output a short
summary of how to write your program if called with the ``--help`` argument
and to output version information if called with the ``--version`` argument.
oranj uses the ``$$help`` and ``$$version`` functions for this.

Unlike many argument parsing systems, these are not generated
programatically; this is due to the author's belief that help text is more
meaningful if a human being wrote it.

Note that the ``$$help`` function parses arguments as well, though not in
as rich a way as the argument parser for ``$$main``: if ``$$help`` takes
``n`` arguments, the first ``n`` command line arguments after the ``--help``
are passed to ``$$help``, and the rest are ignored silently::

    # svn.py

    $$help = fn(subcommand) {
        # Call subcommand help
    }

