A brief introduction
====================

.. index::
    Introduction
    For Programmers

Abstract
--------

All right, so you want to learn oranj. Fine. Just remember that oranj
is not yet done, and so you may at times run into bugs and
errors. Don't worry, they’ll go away soon. In fact, they’ll go away
even sooner if you `report bugs`_. But that’s already getting off track.

Why learn oranj? Well, it’s certainly fun. That was a good enough
reason for me to write it. Don’t like it? Well, think of your own
reason, there are plenty out there.

This brief introduction is intended for programmers. If this is your
first language, feel free to read through, but you might be a bit
confused.

To install oranj, you’ll want to head over to the :doc:`install` page.

.. _`report bugs`: http://github.com/pavpanchekha/oranj/issues

Beginning
---------

Input, output
_____________

::

    io << "Hello, World" << endl

The standard prayer to the programming gods thus completed, we
can move on to other ways of doing input and output. ::

    output("I can say hello, too")

Note that you don’t need a newline at the end. What about input? ::

    name = input("What is your name? ")

With just a prompt, input will return a string, which you store in
name. Now, if you wanted an integer, you might::

    name = io << "What is your age? " >> int

A second argument to input would to the trick too::

    name = input("What is your age? ", int)

In general, ``input`` and ``output`` (as well as
their sister function ``error``, which prints to what C types
would call "stderr") give you more options, while using
``io`` is easier to type and makes C++ programmers feel at home.

While we’re on the topic, let’s cover files::

    f = file("test", "w")
    f.write("Test data")

The ``"w"`` makes the file be opened for writing as
opposed to the default, reading (you can also do ``"a"``
to append. Of course, that’s a rather silly way of doing
things. There are better ones... ::

    f = file("test", "w")
    io.bind(f)
    io << "Hello from io" << endl

``io`` has this useful function called ``bind``,
which will make ``io`` (and ``output``, and
``input``, and ``error``) use the variable passed
for input and output. For example, if you’re using oranj to serve web
pages, ``io`` wouldn’t be the terminal (or your server’s
log), but instead the HTTP stream (actually, ``error`` would
probably be your server’s log file).

Math
____

::
    
    io << 1+2*3/4^5 + 12 000 << endl # Prints 12001.005859

Addition, multiplication, division, exponentiation, and all of their
friends work exactly as expected. Note that you can put spaces into a
number for added readability. Also note that division is
floating-point if necessary. Actually, on the subject of
floating-point... ::

    io << 1/3 << endl # Gives 0.333333
    io << (1/3) * 3 << endl # Gives 1

Floating points will also upconvert (if within 28 decimal points of
precision. At times, this isn’t enough precision, but it’s usually far
more than needed. ::

    io << 17 mod 4 << endl # Gives 1
    io << 5|15 << endl # Gives True

``mod`` is used for modular arithmetic, ``|`` is
used for divisibility-testing (above, it’s asking if 5 divides
15 evenly). ::

    io << inf + 1 << endl # inf

Yes, infinity plus one is infinity

Loops and Such
______________

::

    if inf < 0 {io << "Uh oh!" << endl}

``if`` statements and such don’t require parentheses. In
exchange, the braces are required, even if it's a one-liner. The same
holds for ``while`` and ``for`` statements. ::

    if a == b {
        io <<; "Equal"
    } elif a > b {
        io << "Greater"
    } else {
        io << "Smaller"
    }
    io << endl

``elif`` and ``else`` work as you might
expect. ``elif`` is short for "else if" and basically acts as
a second ``if`` statement that only runs if the first
didn’t. ``else`` is what happens when nothing else does. ::

    a, b = 0, 1
    while a < 1000 {
        a, b = b, a+b
        io << a << endl
    }

The fibonacci numbers always seem the first example of while
statements... I wonder why. In any case, ``while`` loops
are very similar to C ``while`` loops, only you don’t
need the parentheses. Oh, and you can’t do one-liners, just like
with ``if`` statments.

.. code-block:: cpp

    while (a < 10) a++; // Doesn't work in oranj

But hey, its often bad programming style, might annoy you later
on when you actually do need to add braces, and saves you two key
presses (the parentheses) most of the time. ::

    for a in range(10) {
        io << a^2 << " "
    }
    io << endl

``for`` loops work much like they do in Python: they
iterate over a list. In this case, the list is
``range(10)``, which returns ``[0, 1, 2, 3, 4, 5, 6,
7, 8, 9]`` (note that ``0`` is in the range, but 10 is not). You
can use any other list instead::

    for a in [2, 3, 5, 7, 11] {
        io << "Prime! "
    }
    io << endl

In fact, there’s a shortcut if you just want to loop a set number of
times::

    for i in 20 {io << i^2 << endl}

This works because any integer can work as a list, returning the same
values as would a ``range()`` of itself.

Functions
---------

Basic Functions
_______________

::

    hi = fn{io << "Hello, World!" << endl; return}
    hi()

The simplest functions take nothing and return nothing. If you want to
pass arguments... ::

    square = fn(x) {return x^2}

This function takes one argument (``x``) and returns its
square. Now, there are two ways of calling this function::

    square(4) == 4 ! square

The difference is that the second focuses on the value ``4``,
whereas the other on the operation, ``square``. Its sort of
like the distinction between passive and active voice. While "The
firemen saved the boy" and "The boy was saved by the firemen" mean the
same thing, you would use them in different circumstances. Now, what
if you want multiple arguments? ::

    sub = fn "Subtract two numbers" (x, y=1) {
        return x - y
    }

Note that the argument ``y`` has a default value,
``2``, and that the function has a docstring, which is a
short description of what the function does. The key word here is
"short": you shouldn’t describe each argument or the output
format; that should go in the documentation. Instead, you should just
specify the action so that someone reading your code knows what the
function does. ::

    io << (2 ! sub(4)) << endl # Output: -2

In this case, the ``first`` argument is
``2``, not the second. When using the alternative
function call syntax, the argument before the exclamation mark
is always the first argument. (What if you want it to be second?
Then you probably don't want to use the alternative syntax.)

Functions Making Functions
__________________________

::

    adder = fn(x) {
        return fn(y) {return x + y}
    }

The function ``adder`` returns a function. That's right, it’s
a function that returns a function. In this case, the function it
returns has some values "bound": the variable ``x`` is
constant between calls of the internal function. How would you use
this function-of-functions? ::

    add10 = adder(10)
    io << add10(7) << endl # Outputs 17
    io << adder(2)(15) << endl # Outputs 17

Remember that there's nothing really strange going on; you’re just
creating a function, which you can then assign to a variable or call
like any other function. You can, of course use this technique to do
far more complicated things, such as hiding variables where no one can
find them (make them local variables of some particular function that
creates other functions with the variables "embedded"
within) or for using software patterns like the singleton. You can
actually use this for some rather advanced things; see :doc:`lexical-closure-tricks` for some examples.

On the other hand, don't overuse this feature. Every time you
dynamically create a function, you're using up memory. The
``adder`` example is usually (though not always; sometimes
you need a one-argument function) better written as a function of two
arguments.

Remember that in programming, cleverness is often a bad thing, not a
good one.

Functions of Functions
______________________

::

    apply_and_print = fn "Apply function to elements of a list" (l, f) {
        for el in l {
            io << f(el) << " "
        }
        
        io << endl
    }

There’s no reason why a function can’t take another function as an
argument. After all, what would we do with all of the functions we’ve
been making? This example gives the basic idea. We can combine making
and taking functions, too::

    first_arg = fn "Set first argument of a function" (f, arg) {
        return fn(*args, **kwargs) {
            return f(arg, *args, **kwargs)
        }
    }

The idea here should be rather simple: we create a new function
which calls the one we were passed, but inserts in a new argument
in front. The one possibly confusing thing here is the new syntax.
Specifying an asterisk before an argument name (which
**should** be ``args``) makes that argument be a
list of all other arguments (other as in not already used). Two
askerists make it a dictionary of all other keyword arguments. This
lets you create functions with arbitrary numbers of arguments.

