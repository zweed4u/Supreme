import types, functools

def copy_func(f):
    g = types.FunctionType(f.func_code, f.func_globals, name=f.func_name,
                           argdefs=f.func_defaults,
                           closure=f.func_closure)
    g = functools.update_wrapper(g, f)
    return g

def f(x, y=2):
    return x,y

g = copy_func(f)
x = copy_func(f)

print f(1)
print g(3)
print x(2)

assert f is not g
assert f is not x
assert x is not g