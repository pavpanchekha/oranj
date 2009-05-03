import functools
from numpy import *

arange = functools.partial(arange, dtype="float")
array = functools.partial(array, dtype="float")
