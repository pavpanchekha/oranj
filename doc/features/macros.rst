Macros
======

.. index::
    Macro
    FullMacro

What Are Macros?
----------------

Macros are an extremely powerful feature of oranj. At its most
basic, a macro can be viewed simply as a more-general function,
where the generality comes from the fact that a macros arguments
are not evaluated. However, despite this seeming simplicity,
macros can lead to extremely powerful generalizations and abstractions.

Macros (in the sense oranj uses) appeared first in the language lisp,
which adherents call the most powerful and elegant language in the
world. There's something to this. In fact, macros do not appear in
any language but lisp (until now) and so there is some
danger in having oranj considered a new dialect of lisp as opposed
to a language of its own.

As already mentioned, the main difference between a macro and a
function is that a macro does not have its argument evaluated
before the macro is called.

A Simple Macro
______________

::

    oranj> show_ast = fn(x) is Macro {return x}
    oranj> show_ast(a + 1)
    ['OP1', '+', ['IDENT', 'a'], ['PRIMITIVE', ('INT', '1', 10)]]

Above is a very basic macro definition. By adding the ```Macro``
tag to our function, it becomes a macro. As such, when we call it later,
it is passed not the *value* of ``a + 1``, but the parse
tree to it.

Why is this useful? The most basic way you might use a macro is for a
swap function. To do this, however, we need some way to set values
outside the scope of our macro. There are two ways to do this.

``swap`` and Direct Access to ``intp``
________________________________________________________

The first is simply to use the ``intp`` variable to access the
raw interpreter object and set the values there. This can be simplified
by instead using the built-in ``macros`` library::

    import macros
    swap = fn(a, b) is Macro {
        i = macros.Interpreter(intp)
        val1 = i.run(a)
        val2 = i.run(b)
    
        ident1 = a[1]
        ident2 = b[1]
        i.set(ident1, val2)
        i.set(ident2, val1)
    }

There are, however, several problems with this. The first is the lack of
any error correction: what if the arguments passed were not simple
identifiers, but instead some sort of operator? Then we'd be trying to
set the value of "``+``", for example. We'll see how to use
the ``macros`` library's tree-parsing facilities to make this
easier.

```FullMacro``
_______________________

The other option for a swap function is to simply ask the interpreter
to evaluate a some code in the context of the calling function. To make
this easy, the ```FullMacro`` tag exists, which returns not some
specific value but a parse tree, which the interpreter then executes. ::

    import macros
    swap = fn(a, b) is FullMacro {
        i = macros.Interpreter(intp)
        val1 = i.run(a)
        val2 = i.run(b)
        return [["ASSIGN1", a[1], ["VALUE", val2]], ["ASSIGN1", b[1], ["VALUE", val1]]]}
    }

Note the use of the ``"VALUE"`` type of parse tree node to pass
a raw, precomputed value to the oranj interpreter.

Tree Parsing
------------

In the ``swap`` example above, we had a problem in checking
whether the arguments passed to us were really ``"IDENT"``
nodes. The ``macros`` library includes the ``match``
function for just this purpose.

First, let’s try this function on normal lists, and then discuss how to
use it in macros. ::

    oranj> import macros
    oranj> macros.match(["Element1", 1, 2, macros.val("x")], ["Element1", 1, 2, 3])
    ["x": 3]

What the ``macros.match`` function did was use a template (the
first argument) to extract information from a specific list. Now, what
is that "``macros.val("x")</code>``"?

Extractors
__________

::

    oranj> import macros
    oranj> x = macros.val("x")
    oranj> x
    ??x

Huh? ``??x``? Two question marks indeed. Well, it's simple,
really. To continue from the previous example::

    oranj> x is `Extractor
    true
    oranj> x << 3
    3
    oranj> x << ["Lots", ["of", ["complicated": "stuff"]]]
    ['Lots', ['of', ['complicated': 'stuff']]]

So really, a ``macros.val`` object is just some object with
the ```Extractor`` flag and an overridden funnel-in (a.k.a. output)
operator. Oh, and the object has a name parameter::

    oranj> x.name
    'x'

Now, what is the point of adding a name? Because when
``macros.match`` is parsing your list, it will funnel the data
that is in the place of an ```Extractor`` object, and store it
in a dictionary under that object’ s name. That dictionary is eventually
returned to you.

``macros.match`` and Macros
___________________________

::

    import macros
    swap = fn(a, b) is Macro {
        i = macros.Interpreter(intp)
        
        argparse = macros.match([["IDENT", macros.val("a")], ["IDENT", macros.val("b")]], [a, b])
        ident1 = argparse["a"]
        ident2 = argparse["b"]
        
        val1 = i.run(a)
        val2 = i.run(b)
    
        i.set(ident1, val2)
        i.set(ident2, val1)
    }

You can see how we've now extracted the relevant parts of the arguments,
without having to do it manually. In fact, ``macros.match`` will
even raise an ``AssertionError`` if the tree it is given doesn’t
match the template, so we can even claim some amount of error checking.

Common Macro Bugs
-----------------

Well, you can't expect to write perfect code. And due to their lower level
of execution, macros possess several unique types of bugs.

Variable Capture
________________

Mostly prevalent in ```FullMacro`` s, this happens when an internal
variable has the same name as an external one, and so gets overridden. Take,
for example, the following attempt at writing ``swap`` as a
```FullMacro``::

    swap = fn(a, b) is FullMacro {
        return [["ASSIGN1", "t", a],
            ["ASSIGN1", a[1], b],
            ["ASSIGN1", b[1], ["IDENT", "t"]]
    }

This will appear to work, but at some point, disaster will strike::

    oranj> a, b, t = 1, 2, 3
    oranj> swap(a, b)
    oranj> a
    2
    oranj> b
    1
    oranj> t
    1

Oh no! Our macro overwrote the definition of ``t``! How do
we fix this? Well, we could always rename ``t`` to something
more obscure, like "``xasdf235havidu``," but this isn't really
a fix so much as a patch. It’s still possible to overwrite a variable
this way, just far less likely. The solution is to generate a symbol
no one else will use. For this purpose, the ``macros`` library
includes the ``gensym`` function. ::

    oranj> import macros
    oranj> macros.gensym()
    '!!0'
    oranj> macros.gensym()
    '!!1'

"Those aren't valid identifiers," you say. And you're right. But the
oranj interpreter doesn't actually require the identifier to be a valid
one. In fact, it stores some internal state in such "illegal" variables.
The only thing that stops you from using such a variable is that the
parser will complain, because ``!!1`` is indeed not a valid identifier.
All ``gensym`` does is generate such an "illegal" variable,
each time naming it differently (it just increments a counter). So,
every time your macro is invoked, you get a shiny new temporary variable
that interferes with nothing. So, the above ``swap`` macro could
be written as::

    import macros
    swap = fn(a, b) is FullMacro {
        t = macros.gensym()
        return [["ASSIGN1", t, a],
            ["ASSIGN1", a[1], b],
            ["ASSIGN1", b[1], ["IDENT", t]]
    }

Now, there is no danger of interference, because it would be impossible to
define the variable ``!!xxx`` (unless one actively tried to, in
which case they deserve everything they get).

