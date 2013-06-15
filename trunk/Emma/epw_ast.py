

class Ast_Empty():
    def __init__(self):
        pass

    def __repr__(self):
        classname = self.__class__.__name__
        classname = classname.replace('Ast_','')
        return classname+'()'

    def eval(self, env):
        return None


class Ast_Int():
    def __init__(self, i):
        self.i = i

    def __repr__(self):
        classname = self.__class__.__name__
        classname = classname.replace('Ast_','')
        return classname+'(%d)' % self.i

    def eval(self, env):
        return self.i


class Ast_Float():
    def __init__(self, f):
        self.f = f

    def __repr__(self):
        classname = self.__class__.__name__
        classname = classname.replace('Ast_','')
        return classname+'(%f)' % self.f

    def eval(self, env):
        return self.f


class Ast_BinOp():
    def __init__(self, op, l, r):
        self.op = op
        self.l = l
        self.r = r

    def __repr__(self):
        classname = self.__class__.__name__
        classname = classname.replace('Ast_','')
        return classname+'(%s, %s, %s)' % (self.op, self.l, self.r)

    def eval(self, env):
        pass

class Ast_Stmt_List():
    def __init__(self):
        self.node_list = []

    def __repr__(self):
        classname = self.__class__.__name__
        classname = classname.replace('Ast_','')
        return classname + repr(tuple(self.node_list))

    def append(self, ast_node):
        self.node_list.append(ast_node)

    def eval(self, env):
        pass

class Ast_Statement():
    def __init__(self, ast_node):
        self.node = ast_node

    def __repr__(self):
        classname = self.__class__.__name__
        classname = classname.replace('Ast_','')
        return classname + repr(self.node)

    def eval(self, env):
        return None


class Ast_File():
    def __init__(self):
        self.node_list = []

    def __repr__(self):
        classname = self.__class__.__name__
        classname = classname.replace('Ast_','')
        return classname + repr(tuple(self.node_list))

    def append(self, ast_node):
        self.node_list.append(ast_node)

    def eval(self, env):
        pass




