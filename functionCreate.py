import types, functools

def copy_func(f):
    g = types.FunctionType(f.func_code, f.func_globals, name=f.func_name,
                           argdefs=f.func_defaults,
                           closure=f.func_closure)
    g = functools.update_wrapper(g, f)
    return g