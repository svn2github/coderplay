import sys
from epw_env import Environment
from epw_interpreter import *

class Eval_Res(object):
    def __init__(self):
        self.rlist = []

    def __repr__(self):
        if len(self.rlist) == 0:
            return ''
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
                out = ''

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
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname+'(%d)' % self.value

    def eval(self, env):
        return self.value


class Ast_Float(Ast_NYI):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname+'(%f)' % self.value

    def eval(self, env):
        return self.value


class Ast_String(Ast_NYI):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname+'(%s)' % self.value

    def eval(self, env):
        return self.value


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
            raise EvalError('Variable Not Defined', self.name)
        return theEnv.get(self.name)


class Ast_Slice(Ast_NYI):
    def __init__(self):
        self.variable = None
        self.slice = None

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + '(' + repr(self.variable) + ', ' + repr(self.slice) + ')'

    def eval(self, env):
        var = self.variable.eval(env)
        slice = self.slice.eval(env)
        return eval('var' + slice)


class Ast_IdxList(Ast_NYI):
    def __init__(self):
        self.start = None 
        self.end = None
        self.step = None

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        out = ', '.join([repr(self.start),repr(self.end),repr(self.step)])
        return classname + '(' + out + ')'
    
    def eval(self,env):
        start = self.start.eval(env)
        end = self.end.eval(env) if self.end else None
        step = self.step.eval(env) if self.step else None
        ret = '[' + str(start)
        if end is not None or step is not None:
            ret += ':'
            if end is not None:
                ret += str(end)
            if step is not None:
                ret += ':' + str(step)
        ret += ']'
        return ret

class Ast_FuncCall(Ast_NYI):
    def __init__(self):
        self.name = None
        self.arglist = None

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + '(' + repr(self.name) + ', ' + repr(self.arglist) + ')'

    def eval(self, env):
        if self.name.name == 'debug':
            env.top().set('$DEBUG',  1-env.top().get('$DEBUG'))
            return None

        # Get the func definition
        func_name = self.name.name
        if env.has(func_name):
            func_def = env.get(self.name.name)
        else:
            raise EvalError('Undefined Function', func_name)

        # Plug the arglist
        callee_env = func_def['env']
        parmlist = func_def['parmlist']
        plug_arglist(parmlist, self.arglist, env, callee_env)
        
        # Evaluation
        try:
            ret = None
            ret = func_def['body'].eval(callee_env)
        except ReturnControl as e:
            pass

        return ret


class Ast_ArgList(Ast_NYI):
    def __init__(self):
        self.args = []
        self.kwargs = []

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + repr(tuple(self.args+self.kwargs)).replace(',)', ')')

    def append(self, node, is_kwarg=0):
        if is_kwarg:
            self.kwargs.append(node)
        else:
            self.args.append(node)

    def eval(self, env):
        pass


class Ast_KeywordParm(Ast_NYI):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + '(' + repr(self.name) + ', ' + repr(self.value) + ')'

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
            return self.operand.eval(env)
        elif self.op == '-':
            return -self.operand.eval(env)
        elif self.op == 'not':
            return 1 if not self.operand.eval(env) else 0
        else:
            raise EvalError('Unrecognized Unary Operator', self.op)


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
        elif self.op == '%':
            return self.l.eval(env) % self.r.eval(env)
        elif self.op == '>':
            return self.l.eval(env) > self.r.eval(env)
        elif self.op == '<':
            return self.l.eval(env) < self.r.eval(env)
        elif self.op == '>=':
            return 1 if self.l.eval(env) >= self.r.eval(env) else 0
        elif self.op == '<=':
            return 1 if self.l.eval(env) <= self.r.eval(env) else 0
        elif self.op == '==':
            return 1 if self.l.eval(env) == self.r.eval(env) else 0
        elif self.op == '!=':
            return 1 if self.l.eval(env) != self.r.eval(env) else 0
        elif self.op == 'and':
            return 1 if self.l.eval(env) and self.r.eval(env) else 0
        elif self.op == 'or':
            return 1 if self.l.eval(env) or self.r.eval(env) else 0
        elif self.op == 'xor':
            return 1 if not (self.l.eval(env) or self.r.eval(env)) else 0

        # The assignment 
        # Can only assign to a variable
        elif self.op == '=':
            #return env.set(self.l.name, self.r.eval(env))
            pass

        else:
            raise EvalError('Unrecognized Binary Operator', self.op)


class Ast_Print(Ast_NYI):
    def __init__(self):
        self.node_list = []

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + repr(tuple(self.node_list)).replace(',)', ')')

    def append(self, ast_node):
        self.node_list.append(ast_node)

    def eval(self, env):
        if len(self.node_list) > 0: # in case it is an empty print
            sys.stdout.write(str(self.node_list[0].eval(env)))
        for node in self.node_list[1:]:
            sys.stdout.write(' ')
            sys.stdout.write(str(node.eval(env)))
        sys.stdout.write('\n')
        return None


class Ast_DefFunc(Ast_NYI):
    def __int__(self):
        self.name = None
        self.parmlist = None
        self.body = None

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        out = ', '.join([repr(self.name), repr(self.parmlist), repr(self.body)])
        return classname + '(' + out + ')'

    def eval(self, env):
        func_env = Environment(outer=env)
        if self.parmlist:
            for arg in self.parmlist.args:
                func_env.set(arg.name)
            for kwarg in self.parmlist.kwargs:
                func_env.set(kwarg.name.name, kwarg.value.eval(env))
        env.set(self.name.name, {'body': self.body, 'env': func_env, 'parmlist': self.parmlist})

class Ast_WhileLoop(Ast_NYI):
    def __init__(self):
        self.predicate = None
        self.body = None

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + '(' + repr(self.predicate) + ', ' + repr(self.body) +')'

    def eval(self, env):
        ret = None
        while self.predicate.eval(env):
            try:
                ret = self.body.eval(env)
            except BreakControl as e:
                break
            except ContinueControl as e:
                continue
        return ret if ret else None


class Ast_ForLoop(Ast_NYI):
    def __init__(self):
        self.counter = None
        self.start = None
        self.end = None
        self.step = Ast_Int(1) # default step
        self.body = None

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        out = ', '.join([repr(self.counter),repr(self.start),repr(self.end),repr(self.step),repr(self.body)])
        return classname + '(' + out + ')'

    def eval(self, env):
        if env.has(self.counter.name):
            ii = env.get(self.counter.name)
        else:
            env.set(self.counter.name)
        ret = None
        for ii in range(self.start.eval(env), self.end.eval(env)+1, self.step.eval(1)):
            env.set(self.counter.name, ii)
            try:
                ret = self.body.eval(env)
            except BreakControl as e:
                break
            except ContinueControl as e:
                continue
        #raise Exception
        return ret if ret else None


class Ast_Continue(Ast_NYI):
    def eval(self, env):
        raise ContinueControl()

class Ast_Break(Ast_NYI):
    def eval(self, env):
        raise BreakControl()

class Ast_Return(Ast_NYI):
    def eval(self, env):
        raise ReturnControl()


class Ast_If(Ast_NYI):
    def __init__(self):
        self.predicate = None
        self.if_body = None
        self.else_body = None

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + repr((self.predicate, self.if_body, self.else_body)).replace(',)', ')')

    def eval(self, env):
        if self.predicate.eval(env):
            return self.if_body.eval(env)
        if self.else_body is not None:
            return self.else_body.eval(env)
        else:
            return None


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
        ret = Eval_Res()
        for node in self.node_list:
            ret.append(node.eval(env))
        return ret


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
        ret = Eval_Res()
        for node in self.node_list:
            ret.append(node.eval(env))
        return ret


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




def plug_arglist(parmlist, arglist, caller_env, callee_env):
    if parmlist is None and arglist is not None:
        raise EvalError('Unmatched Function Parameters', [parmlist, arglist])
    if arglist is None:
        return
    if len(parmlist.args) < len(arglist.args) or len(parmlist.kwargs) < len(arglist.kwargs):
        raise EvalError('Unmatched Function Parameters', [parmlist, arglist])

    # plug positional arguments
    for ii in range(len(arglist.args)):
        parmname = parmlist.args[ii].name
        callee_env.set(parmname, arglist.args[ii].eval(caller_env))

    # plug keyword arguments





