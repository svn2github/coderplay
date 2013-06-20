import sys
from epw_env import Environment, get_topenv
from epw_interpreter import *
from epw_builtin import *


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
        self.collection = None
        self.idxlist = None

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + '(' + repr(self.collection) + ', ' + repr(self.idxlist) + ')'

    def eval(self, env):
        var = self.collection.eval(env)
        if type(var) != list:
            raise EvalError('Can Only Slice a List', str(var))
        idxlist = self.idxlist.eval(env)
        try: 
            return var[idxlist]
        except IndexError:
            raise EvalError('List Index Out of Range', '')


class Ast_IdxList(Ast_NYI):
    def __init__(self):
        self.start = None 
        self.end = None
        self.step = None
        self.nColon = 0

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        out = ', '.join([repr(self.start),repr(self.end),repr(self.step)])
        return classname + '(' + out + ')'
    
    def eval(self,env):
        start = self.start.eval(env) if self.start else None
        end = self.end.eval(env) if self.end else None
        step = self.step.eval(env) if self.step else None
        if self.nColon == 0:
            return start
        elif self.nColon == 1:
            return slice(start, end)
        elif self.nColon == 2:
            return slice(start, end, step)
            

class Ast_FuncCall(Ast_NYI):
    def __init__(self):
        self.func = None
        self.arglist = None

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + '(' + repr(self.func) + ', ' + repr(self.arglist) + ')'

    def eval(self, caller_env):
        # Get the top env
        topenv = get_topenv()

        func = self.func
        # If the function call is a simple ID() form, we check whether it 
        # is a builtin function.
        # or get its definition from topenv.
        # This is not ideal, but since the language does not allow assign
        # another variable name to a builtin function. So it may work for
        # now.
        if repr(func).find('Variable(') == 0:
            # Check and run if its a builtin func
            flag, ret = try_builtin_func(self, caller_env)
            if flag: return ret

            # Otherwise, Get the func definition from top level
            name = func.name
            if topenv.has(name):
                func_def = get_topenv().get(name)
            else:
                raise EvalError('Undefined Function', name)
        else:
            func_def = func.eval(caller_env)

        # Plug the arglist
        callee_env = Environment(outer=caller_env)
        plug_arglist(func_def, self.arglist, caller_env, callee_env)
        
        # Evaluation
        try:
            ret = None
            ret = func_def['body'].eval(callee_env)
        except ReturnControl as e:
            if len(e.args) > 0:
                ret = e.args[0]

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
        self.parm_name = name
        self.value = value

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname + '(' + repr(self.parm_name) + ', ' + repr(self.value) + ')'

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
        try:
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
                return 1 if bool(self.l.eval(env)) != bool(self.r.eval(env)) else 0

            else:
                raise EvalError('Unrecognized Binary Operator', '')

        except TypeError as e:
            raise EvalError(e.message, self.op)


class Ast_Assign(Ast_NYI):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        return classname+'(%s, %s)' % (self.left, self.right)

    def eval(self, env):
        # It seems either IPython or Python has a bug to not being able to
        # correctly run isinstance in the subsequent sessions after an error 
        # out. So we are using an ugly workaround.

        #if isinstance(self.left, Ast_Variable):
        if repr(self.left).find('Variable(') == 0:
            # this is a simple scalar variable
            return env.set(self.left.name, self.right.eval(env))

        #elif isinstance(self.left, Ast_Slice):
        elif repr(self.left).find('Slice(') == 0:
           
            # this can be either an list variable or function that yields
            # list like variable. In either case we can use the result
            # from eval directly since it is a reference.
            var = self.left.collection.eval(env)
            idxlist = self.left.idxlist.eval(env)
            value = self.right.eval(env)
            var[idxlist] = value
            return value

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
        self.func = None
        self.parmlist = None
        self.body = None

    def __repr__(self):
        classname = super(self.__class__, self).__repr__()
        out = ', '.join([repr(self.func), repr(self.parmlist), repr(self.body)])
        return classname + '(' + out + ')'

    def eval(self, env):
        # Function can only be defined at the Top Level
        if env != get_topenv():
            raise EvalError('Function Definition Can Only Be at Top Level', '')
        # Process any parameter list
        if self.parmlist:
            pos_parmlist = []
            for arg in self.parmlist.args:
                pos_parmlist.append(arg.name)
            kw_parmlist = {}
            for kwarg in self.parmlist.kwargs:
                kw_parmlist[kwarg.parm_name.name] = kwarg.value.eval(env)
        # Create the function definition and store in the top level 
        func_def = {'body': self.body, 
                    'pos_parmlist': pos_parmlist, 'kw_parmlist': kw_parmlist}
        env.set(self.func.name, func_def)
        return func_def

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
    def __init__(self, node=None):
        self.ret = node

    def eval(self, env):
        raise ReturnControl(self.ret.eval(env))


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
        ret = None
        top_env = get_topenv()
        for node in self.node_list:
            ret = node.eval(env)
            # Set value for magic variable
            if ret is not None:
                top_env.set('_', ret)
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
        ret = None
        for node in self.node_list:
            ret = node.eval(env)
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



def plug_arglist(func_def, arglist, caller_env, callee_env):

    pos_parmlist = func_def['pos_parmlist']
    pos_arglist = arglist.args
    if len(pos_parmlist) < len(pos_arglist):
        raise EvalError('Unmatched Function Positional Parameters', 
                        [pos_parmlist, pos_arglist])

    kw_parmlist = func_def['kw_parmlist']
    kw_arglist = {}
    for kwarg in arglist.kwargs:
        kw_arglist[kwarg.parm_name.name] = kwarg.value.eval(caller_env)

    if not set.issubset(set(kw_arglist.keys()), set(kw_parmlist.keys())):
        raise EvalError('Unmatched Function Keyword Parameters', '')

    # plug positional arguments
    for ii in range(len(pos_parmlist)):
        value = pos_arglist[ii].eval(caller_env) if ii < len(pos_arglist) else None
        callee_env.set(pos_parmlist[ii], value)

    # plug keyword arguments
    for key in kw_parmlist.keys():
        value = kw_arglist[key] if key in kw_arglist.keys() else kw_parmlist[key]
        callee_env.set(key, value)



