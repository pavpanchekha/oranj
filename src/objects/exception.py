from orobject import OrObject

class OrException(OrObject, Exception):
    class_name = "Exception"

    def __init__(self, *args, **kwargs):
        OrObject.__init__(self, "", OrException)
        
        self.args = args
        self.kwargs = kwargs
        self.traceback = []
        
        self.set("traceback", self.traceback)
        self.set("args", self.args)
        self.set("kwargs", self.kwargs)
    
    def __str__(self):
        c = self.get("$$class")
        c = c.class_name if hasattr(c, "class_name") else c.__name__
        return "%s: %s" % (c, str(args[0]))
    
    def __repr__(self):
        return "<" + c + " '" + str(self.args[0]) + "'>"

OrObject.register(OrException, Exception)
