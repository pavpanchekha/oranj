
class ErrorContext:
    def __init__(self, active=True):
        self.messages = []
        self.path = [self.messages]
        self.active = active
        self.topop = False
    
    def __nonzero__(self):
        return bool(self.active and self.messages)
    
    def clear(self):
        self.messages = []
        self.path = [self.messages]
        self.topop = False
    
    def write(self, message, level="message"):
        if not self.active: return
        if self.topop: self.pop(*self.topop)
        
        if level == "data":
            self.path[-1].append(("data", message))
        else:
            self.path[-1].append(message)
    
    def push(self, message=None, level=None):
        if message:
            self.write(message, level)
        
        self.path[-1].append([])
        self.path.append(self.path[-1][-1])
    
    def pop(self, message=None, level=None, certain=True):
        if not certain:
            self.topop = (message, level)
            return

        self.topop = False
        self.path.pop()
        
        if len(self.path):
            self.path[-1].pop()
        else:
            self.messages = []
            self.path = [self.messages]
        
        if message:
            self.write(message, level)
    
    def str(self, data=False):
        """ If data is True, display along with rest. If data is callable,
        call it with data as input and use return value. """
        
        lines = ErrorContext.__write_tree(self.messages, data=data)
        return "\n".join(lines)
    
    def __str__(self):
        return self.str()
    
    @staticmethod
    def __write_tree(tree, tab=0, l=None, data=False):
        if l is None:
            l = [] # Because default arguments are evaluated once!
        
        for i in tree:
            if type(i) == type([]):
                ErrorContext.__write_tree(i, tab + 1, l, data)
            elif type(i) == type(()) and len(i) == 2 and i[0] == "data":
                if data == True:
                    l.append("===========Data block===========\n" + repr(i[1]) + "\n===========End data block=======")
                elif callable(data):
                    l.append(data(i[1]))
            else:
                l.append("\t"*tab + str(i))

        return l
