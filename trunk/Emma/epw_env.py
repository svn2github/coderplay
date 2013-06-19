'''
The runtime environment.
'''

class Environment(object):
    def __init__(self, parms=(), args=(), outer=None):
        self.binding = {}
        self.binding.update(zip(parms, args))
        self.outer = outer

    def update(self, arg):
        self.binding.update(arg)

    def find(self, name):
        'Find the innermost Environment where name exists'
        if name in self.binding:
            return self
        else:
            if self.outer is not None:
                return self.outer.find(name)
            else:
                return None

    def top(self):
        'Get the top Environment'
        if self.outer is not None:
            return self.outer.top()
        else:
            return self

    def get(self, name):
        'Get the name from this Environment'
        return self.binding[name]

    def set(self, name, value=None):
        'Set the named variable in this Environment'
        self.binding[name] = value
        return value

    def has(self, name):
        return 1 if name in self.binding else 0


topenv = Environment()

def get_topenv():
    return topenv

