
import core
import core.objects.about
import os as _os
import sys as _sys


k = _os.path.abspath(__file__)[:-12]
core.objects.about.mainpath = _os.path.join(k, "core/")
_sys.path.insert(0, _os.path.join(k, "core", "lib"))
_sys.path.append(_os.path.join(k, "build"))

