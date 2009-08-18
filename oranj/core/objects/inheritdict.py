# -*- coding: utf-8 -*-
class InheritDict:
    def __init__(self, *parents):
        self.parents = parents
        self.dict = {}

    def update(self, keys={}):
        self.dict.update(keys)

    def __getitem__(self, key):
        if key in self.dict:
            return self.dict[key]
        elif len(self.parents) == 1:
            return self.parents[0][key]
        else:
            for i in self.parents:
                try:
                    a = i[key]
                except (KeyError, TypeError):
                    pass

        try:
            self[key] = a # Cache lookup
            return a
        except NameError:
            raise KeyError("Key not in InheritDict: " + str(key))

    def __setitem__(self, key, value):
        self.dict[key] = value

    def __delitem__(self, key):
        del self.dict[key]

    def __contains__(self, key):
        return key in self.dict or self.parents and any(key in i for i in self.parents)

    def __str__(self):
        return "[" + str(self.dict)[1:-1] + "]"

    def __repr__(self):
        return str(self)

    def keys(self):
        return self.dict.keys() + sum([i.keys() for i in self.parents], [])

    def values(self):
        return self.dict.values() + sum([i.values() for i in self.parents], [])

    def items(self):
        return self.dict.items() + sum([i.items() for i in self.parents], [])
