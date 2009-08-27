from number import Number
from orobject import OrObject

inf = Number("Infinity")
true = OrObject.from_py(True)
false = OrObject.from_py(False)
nil = OrObject.from_py(None)

true.set("$$str", lambda: "true")
true.set("$$repr", lambda: "true")
false.set("$$str", lambda: "false")
false.set("$$repr", lambda: "false")
nil.set("$$str", lambda: "nil")
nil.set("$$repr", lambda: "nil")

OrObject.register(lambda x: true if x else false, type(True))
OrObject.register(lambda x: nil, type(None))
