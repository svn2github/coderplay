
builtin_func_def = {
    'list': ((0, 1), None),
    'debug': ((0, 0), None),
}

builtin_func_names = builtin_func_def.keys()

def check_builtin_func_usage(func_node):

    func_name = func_node.func_name.name
    if func_name not in builtin_func_names:
        return 1
    else:
        nargs = len(func_node.arglist.args)
        range = builtin_func_def[func_name][0]
        if nargs >= range[0] and nargs <= range[1]:
            return 1
        else:
            return 0
