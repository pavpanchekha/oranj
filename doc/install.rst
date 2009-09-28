Installation
============

.. index::
    Installation

Stable Release
--------------

To install oranj, you first need a python installation. oranj works on python versions 2.5 and higher in
the python 2.x series. A Python 3.0 or higher installation *will not* work. Python can be
downloaded from `python.org`_. oranj does not require any modules
not found in the python standard library to work properly.

Stable releases of oranj are available in the `github downloads section`_. You most likely want the RPM Package, Debian Package, or Windows Installer.
These are installed in the normal way. The Zip and Tarballs contain source code that you will have to
install by hand; run:

.. code-block:: sh

    sudo python setup.py install

.. _`python.org`: http://python.org/download
.. _`github downloads section`: http://github.com/pavpanchekha/oranj/downloads

replacing ``sudo`` with your favorite way of becoming root.

This will work on all major operating systems (tested: Windows, Fedora & Ubuntu Linux).

Development (Unstable)
----------------------

For the intrepid users or budding oranj developers, the current unstable version of oranj can be downloaded
from github using the git version control system. If git is installed on your computer, this can be accomplished
simply by running:

.. code-block:: sh

    git clone git://github.com/pavpanchekha/oranj.git

If you do not have git and have no need to develop oranj yourself, you can use github's compressed file service
to get the current version of oranj: `zip`_ or
`tarball`_.

The source code can then be installed with:

.. code-block:: sh

    sudo python setup.py install

replacing ``sudo`` with your favorite way of becoming root.

.. _`zip`: http://github.com/pavpanchekha/oranj/zipball/master
.. _`tarball`: http://github.com/pavpanchekha/oranj/tarball/master
