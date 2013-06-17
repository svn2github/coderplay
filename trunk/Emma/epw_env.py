'''
The runtime environment.
'''

class Environment(dict):
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, name):
        'Find the innermost Environment where name exists'
        if name in self:
            return self
        else:
            if self.outer is not None:
                return self.outer.find(name)
            else:
                return None
    def top(self):
        if self.outer is not None:
            return self.outer.top()
        else:
            return self


