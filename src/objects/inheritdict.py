

class InheritDict:
    def __init__(self, parent=None):
        self.parent = parent
        self.dict = {}

    def update(self, keys={}):
        self.dict.update(keys)

    def __getitem__(self, key):
        if key in self.dict:
            return self.dict[key]
        else:
            try:
                a = self.parent[key]
                self[key] = a # Cache lookup
                return a
            except TypeError:
                raise AttributeError("Key not in InheritDict: " + key)

    def __setitem__(self, key, value):
        self.dict[key] = value

    def __delitem__(self, key):
        del self.dict[key]

    def __contains__(self, key):
        return key in self.dict or self.parent and key in self.parent

    def keys(self):
        if self.parent:
            return list(self.dict.keys()) + self.parent.keys()
        else:
            return list(self.dict.keys())
