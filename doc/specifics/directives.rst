Directives and Inline Blocks
============================

Directives
----------

Oranj directives are special commands to the interpreter. There are no
fundamental differences between directives and other statements; its just
that directives usually represent code that causes the interpreter to do
something special.

The critical point is that processing directives 1) can be modified within the
program (in fact, you can add your own) and 2) are not guaranteed to work
across oranj runtimes. Which directives to include varies across runtimes because
some may be extremely difficult to implement on a particular runtime (for example,
a compiler for oranj would not, most likely, allow the ``#!drop``
directive, as that would require adding the whole of oranj into your executable).

All directives take the form::

    #!name [arg arg arg ...]

where the arguments are parsed according to shell command syntax. Thus, ::

    #!ec data "Hello there!"

is a directive (``ec``) with two arguments.

Directives return values. Thus, the following is a perfectly valid command::

    my_ec = #!ec

The following directives are implemented:

``#!clear``
___________

Clears the screen. Particularly useful in the interactive console. PLEASE
do not use as a method of clearing the screen within your program; it's meant
only as a convenience.

``#!drop`` and ``#!undrop``
___________________________

Drop down to an oranj shell. This is useful to debug your scripts::

    if bad_thing {
        term << "Dropping down to shell. Why is bad_thing true?"
        #!drop
    }

``#!drop`` can be used inside a regular shell; it'll just be rather
strange. The result is just another, new, shell, which'll look identical to
the one above but won't be. After dropping down into a shell, ``#!undrop``
is used to exit it and continue the code ``#!drop`` ed from.

``#!pydrop`` and ``undrop()``
_____________________________

Drop down to a python shell. The variable ``intp`` is the interpreter
instance that ``#!pydrop`` was called from. Usefull to debug the oranj
interpreter and perhaps for deep debugging of oranj source code.

``undrop()`` will return to the oranj interpreter.

``#!pyerror``
_____________

Print out the python stack trace of the last exception. Mostly useful for debugging
the oranj interpreter itself.

``#!set variable value``
________________________

Set a global interpreter option. Options:

ec
    Set to on to enable context logging, off to disable

``#!debug`` and ``#!step [cmd]``
________________________________

``#!debug`` starts up the built-in debugger, thus acting much like a
breakpoint in most IDEs. Before any line of code is executed,
it will be printed to the console and an oranj shell will be launched, where you
can do more or less anything to the running program (check the values of variables,
change those values, run other directives).

``#!step`` is used to control the debugging process. If called without
arguments, it simply steps one statement forward through the code. The commands
``out`` and ``in`` will dictate whether you will "go into" functions. Each ``#!step in``
increases how many function calls in the debugger will go, and each
``#!step out`` decreases it.

One can also stop the debugger (and let the program finish running as normal)
with ``#!step end``. Note that the real reason for having these commands
is to make it easy for IDEs to include graphical debuggers. Most likely, an IDE
will provide a much more convenient way to debug your program than the raw
interpreter directives.

``#!ec``
________

Logs its arguments to the :doc:`/features/errorcontext`.
If argument begins with ``data``, rest of arguments evaluated and added
as a data message. For example::

    #!ec Retrieving data from internet
    url_data = url_get("http://www.google.com")
    #!ec data url_data

If no arguments are passed, the directive returns the error context object.
  
``#!exit``
__________

Exits the oranj program or shell. Please *do not* use it to exit from
a program. There are better ways (for example, ``intp.quit()``) that'll
ensure portability across versions of oranj.

Inline Blocks
-------------

Inline blocks in oranj are a block of code that the interpreter does
not parse, but instead executes as a unit. This is most commonly used
to run commands in a different programming language.

Just like processing directives, these are not guaranteed to work across
oranj implementations. For example, most oranj implementations would not
include the ``#!python { #! }`` directive.

Also like directives, oranj processing blocks can return values, which can
be assigned just like the results of oranj directives.

All inline blocks take the form

::

    #!name [arg, arg, arg, ...] {
    text ...
    #! }

Where the actual code is in the space labelled text. Lines of the form
"``#!...``" cannot be used within an inline block. The following block types
are implemented:

``#!python { #! }``
___________________

This block will execute a unit of code in a python interpreter. The
code can make use of the Interpreter object, which can be retrieved from
the global object ``intp``. To interact with variable defined within oranj,
use ``intp.curr`` as a dictionary. Make sure to call
``OrObject.from_py`` on any object that is exported to the running
oranj code. The result of the python block (typically, the value of the last
expression evaluated) will be made into an ``OrObject`` for you and
be returned to the oranj code.

``#!xml { #! }``
________________

The contents of the block will be parsed as XML and be returned as an
``xml.etree.ElementTree.ElementTree`` object. Read the `ElementTree Documentation`_
for more.

.. _`ElementTree Documentation`: http://docs.python.org/library/xml.etree.elementtree.html#xml.etree.ElementTree.ElementTree

``#!nil { #! }``
________________


Nothing will be done with the contents of the block. Use as a multiline
comment.

``#!output { #! }``
___________________

Contents of block are output to whatever ``io`` is bound to.

Custom Directives and Blocks
----------------------------

TODO: Fill in

