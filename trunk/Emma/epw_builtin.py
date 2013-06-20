from epw_env import get_topenv

builtin_func_def = {
    'list': ((0, 1), None),
    'debug': ((0, 0), None),
}

builtin_func_names = builtin_func_def.keys()

def try_builtin_func(func_node, caller_env):

    func = func_node.func

    # if not a builtin func, we do not check
    name = func.name
    if name not in builtin_func_names:
        return (0, 0)

    else:
        nargs = len(func_node.arglist.args)
        range = builtin_func_def[name][0]
        if nargs < range[0] or nargs > range[1]:
            raise EvalError('Incorrect Parameters for Builtin Function', 
                            name)

    topenv = get_topenv()
    if name == 'debug':
        topenv.set('$DEBUG',  1-topenv.get('$DEBUG'))
        return (1, None)

    elif name == 'list':
        if len(func_node.arglist.args) == 0:
            return (1, [])
        else:
            return (1, [0] * func_node.arglist.args[0].eval(caller_env))
