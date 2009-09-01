from orobject import OrObjec
from collections import OrderedDict

class ODict(OrderedDict):
    def __init__(self, dict=[], **kwargs):
        if isinstance(dict, OrderedDict):
            dict = dict.items()
        
        OrderedDict.__init__(self, dict + kwargs.items())
    
    def ispy(self): return True
    def topy(self): return self
    
    def __str__(self, fn=str):
        return "{%s}" % ", ".join(
            map(lambda x: ": ".join(map(fn, x)),
                self.items()))
    
    def __repr__(self):
        return self.__str__(repr)

OrObject.register(ODict, OrderedDict)
