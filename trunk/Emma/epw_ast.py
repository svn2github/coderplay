import sys

class EvalError(Exception):
    pass

class Eval_Res(object):
    def __init__(self):
        self.rlist = []

    def __repr__(self):
        if len(self.rlist) == 0:
            return None
        else:
            out = ''
            valid = 0
            if self.rlist[0] is not None:
                out += str(self.rlist[0])
                valid = 1

            for res in self.rlist[1:]:
                if res is not None:
                    if out != '': out += '\n'
                    out += str(res)
                    valid = 1

            if not valid:
                out = None

            return out


    def append(self, res):
        self.rlist.append(res)


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


class Ast_String(Ast_NYI):
    def __init__(self, a_string):
        self.a_string = a_string

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname+'(%s)' % self.a_string

    def eval(self, env):
        return self.a_string


class Ast_Variable(Ast_NYI):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname+'(%s)' % self.name

    # NOTE the self.name is not evaluated. So it allows ONLY literal 
    # variable name.
    def eval(self, env):
        theEnv = env.find(self.name)
        if theEnv is None:
            raise EvalError('Variable not defined', self.name)
        return theEnv[self.name]


class Ast_ArrayElement(Ast_NYI):
    def __init__(self):
        self.name = None
        self.slice = None

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + '(' + repr(self.name) + ', ' + repr(self.slice) + ')'

    def eval(self, env):
        pass


class Ast_SliceList(Ast_NYI):
    def __init__(self):
        self.start = 0
        self.end = -1
        self.step = 1

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        out = ', '.join([repr(self.start),repr(self.end),repr(self.step)])
        return classname + '(' + out + ')'
    
    def eval(self,env):
        pass


class Ast_FuncCall(Ast_NYI):
    def __init__(self):
        self.name = None
        self.args = None

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + '(' + repr(self.name) + ', ' + repr(self.args) + ')'

    def eval(self, env):
        if self.name == 'debug':
            env.top()[self.args[1].eval(env)] = self.args[2].eval(env)


class Ast_ArgList(Ast_NYI):
    def __init__(self):
        self.args = []

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + repr(tuple(self.args)).replace(',)', ')')

    def append(self, node):
        self.args.append(node)

    def eval(self, env):
        pass


class Ast_UnaryOp(Ast_NYI):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname+'(%s, %s)' % (self.op, self.operand)

    def eval(self, env):
        if self.op == '+':
            return self.operand
        elif self.op == '-':
            return -self.operand
        elif self.op == 'not':
            return not self.operand
        else:
            sys.stderr.write('Unrecognized operator '+self.op+'\n')
            sys.exit(1)


class Ast_BinOp(Ast_NYI):
    def __init__(self, op, l, r):
        self.op = op
        self.l = l
        self.r = r

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname+'(%s, %s, %s)' % (self.op, self.l, self.r)

    def eval(self, env):
        # TODO: Still need to work on coerce
        if self.op == '+':
            return self.l.eval(env) + self.r.eval(env)
        elif self.op == '-':
            return self.l.eval(env) - self.r.eval(env)
        elif self.op == '*':
            return self.l.eval(env) * self.r.eval(env)
        elif self.op == '/':
            return self.l.eval(env) / self.r.eval(env)
        elif self.op == '>':
            return self.l.eval(env) > self.r.eval(env)
        elif self.op == '<':
            return self.l.eval(env) < self.r.eval(env)
        elif self.op == '>=':
            return self.l.eval(env) >= self.r.eval(env)
        elif self.op == '<=':
            return self.l.eval(env) <= self.r.eval(env)
        elif self.op == '==':
            return self.l.eval(env) == self.r.eval(env)
        elif self.op == '!=':
            return self.l.eval(env) != self.r.eval(env)
        elif self.op == 'and':
            return self.l.eval(env) and self.r.eval(env)
        elif self.op == 'or':
            return self.l.eval(env) or self.r.eval(env)
        elif self.op == 'xor':
            return not (self.l.eval(env) or self.r.eval(env))

        # The ristrication here is that ONLY a variable name can be used as
        # the left side for an assignment. It won't currently allow an array
        # subscript or a function call to be on the left side. NOTE the 
        # self.l is not evaluated. So it can ONLY be a literal variable name.
        # The parser won't allow them either.
        elif self.op == '=':
            env[self.l] = self.r.eval(env)

        else:
            sys.stderr.write('Unrecognized operator '+self.op+'\n')
            sys.exit(1)



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
            sys.stdout.write(str(self.node_list[0].eval(env)))
        for node in self.node_list[1:]:
            sys.stdout.write(' ')
            sys.stdout.write(str(node.eval(env)))
        sys.stdout.write('\n')
        return None


class Ast_DefFunc(Ast_NYI):
    def __int__(self):
        self.name = None
        self.args = None
        self.body = None

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        out = ', '.join([repr(self.name), repr(self.args), repr(self.body)])
        return classname + '(' + out + ')'

class Ast_WhileLoop(Ast_NYI):
    def __init__(self):
        self.condition = None
        self.body = None

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + '(' + repr(self.condition) + ', ' + repr(self.body) +')'

    def eval(self, env):
        pass


class Ast_ForLoop(Ast_NYI):
    def __init__(self):
        self.counter = None
        self.start = None
        self.end = None
        self.step = 1 # default step
        self.body = None

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        out = ', '.join([repr(self.counter),repr(self.start),repr(self.end),repr(self.step),repr(self.body)])
        return classname + '(' + out + ')'

    def eval(self, env):
        pass


class Ast_If(Ast_NYI):
    def __init__(self):
        self.node_list = []

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + repr(tuple(self.node_list)).replace(',)', ')')

    def append(self, ast_node):
        self.node_list.append(ast_node)

    def eval(self, env):
        cond = self.node_list[0].eval(env)
        if cond:
            return self.node_list[1].eval(env)
        else:
            return self.node_list[2].eval(env)


class Ast_Stmt_List(Ast_NYI):
    def __init__(self):
        self.node_list = []

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + repr(tuple(self.node_list)).replace(',)', ')')

    def __len__(self):
        return len(self.node_list)

    def append(self, ast_node):
        self.node_list.append(ast_node)

    def eval(self, env):
        res = Eval_Res()
        for node in self.node_list:
            res.append(node.eval(env))
        return res


class Ast_Stmt_Block(Ast_NYI):
    def __init__(self):
        self.node_list = []

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + repr(tuple(self.node_list)).replace(',)', ')')

    def __len__(self):
        return len(self.node_list)

    def append(self, ast_node):
        self.node_list.append(ast_node)

    def eval(self, env):
        res = Eval_Res()
        for node in self.node_list:
            res.append(node.eval(env))
        return res


class Ast_Statement(Ast_NYI):
    def __init__(self, ast_node):
        self.node = ast_node

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + repr(self.node)

    def eval(self, env):
        return self.node.eval(env)


class Ast_File(Ast_NYI):
    def __init__(self):
        self.node_list = []

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + repr(tuple(self.node_list)).replace(',)',')')

    def __len__(self):
        return len(self.node_list)

    def append(self, ast_node):
        self.node_list.append(ast_node)

    def eval(self, env):
        for node in self.node_list:
            node.eval(env)


class Ast_Prompt(Ast_NYI):
    def __init__(self, ast_node):
        self.node = ast_node

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + '(' + repr(self.node) + ')'

    def eval(self, env):
        return self.node.eval(env)



