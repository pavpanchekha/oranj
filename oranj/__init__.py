
import core
import core.objects.about
import os as _os
import sys as _sys

core.objects.about.mainpath = _os.path.abspath(__file__)[:-11] + "core/"
_sys.path.append(_os.path.join(core.objects.about.mainpath, "lib"))
