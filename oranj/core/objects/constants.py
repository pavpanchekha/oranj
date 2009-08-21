from number import Number
from orobject import OrObject

inf = Number("Infinity")
true = OrObject.from_py(True)
false = OrObject.from_py(False)
nil = OrObject.from_py(None)

true.__str__ = lambda: "true"
true.__repr__ = lambda: "true"
false.__str__ = lambda: "false"
false.__repr__ = lambda: "false"
nil.__str__ = lambda: "nil"
nil.__repr__ = lambda: "nil"

OrObject.register(lambda x: true if x else false, type(True))
OrObject.register(lambda x: nil, type(None))
