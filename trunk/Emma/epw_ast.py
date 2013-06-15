import sys

# Generic AST node as Not Yet Implemented
class Ast_NYI(object): 
    def __init__(self):
        pass

    def __repr__(self):
        classname = self.__class__.__name__
        classname = classname.replace('Ast_','')
        return classname

    def eval(self, env):
        return None


class Ast_Int(Ast_NYI):
    def __init__(self, i):
        self.i = i

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname+'(%d)' % self.i

    def eval(self, env):
        return self.i


class Ast_Float(Ast_NYI):
    def __init__(self, f):
        self.f = f

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname+'(%f)' % self.f

    def eval(self, env):
        return self.f

class Ast_Variable(Ast_NYI):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname+'(%s)' % self.name

    def eval(self, env):
        pass


class Ast_UnaryAop(Ast_NYI):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname+'(%s, %s)' % (self.op, self.operand)

    def eval(self, env):
        pass


class Ast_BinAop(Ast_NYI):
    def __init__(self, op, l, r):
        self.op = op
        self.l = l
        self.r = r

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname+'(%s, %s, %s)' % (self.op, self.l, self.r)

    def eval(self, env):
        pass


class Ast_Print(Ast_NYI):
    def __init__(self):
        self.node_list = []

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + repr(tuple(self.node_list)).replace(',)', ')')

    def append(self, ast_node):
        self.node_list.append(ast_node)

    def eval(self, env):
        if len(self.node_list) > 0:
            sys.stdout.write(repr(self.node_list[0].eval(env)))
        for node in self.node_list[1:]:
            sys.stdout.write(' ' + repr(node.eval(env)))
        sys.stdout.write('\n')


class Ast_Stmt_List(Ast_NYI):
    def __init__(self):
        self.node_list = []

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + repr(tuple(self.node_list)).replace(',)', ')')

    def append(self, ast_node):
        self.node_list.append(ast_node)

    def eval(self, env):
        pass


class Ast_Statement(Ast_NYI):
    def __init__(self, ast_node):
        self.node = ast_node

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + repr(self.node)

    def eval(self, env):
        pass


class Ast_File(Ast_NYI):
    def __init__(self):
        self.node_list = []

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + repr(tuple(self.node_list)).replace(',)',')')

    def append(self, ast_node):
        self.node_list.append(ast_node)

    def eval(self, env):
        pass



