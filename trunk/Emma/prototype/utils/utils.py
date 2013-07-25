import os

# the script full name with path
script = os.path.realpath(__file__)

# the root of prototype
fields = script.split(os.path.sep)[0:-3]
epwdir = os.path.sep.join(fields)

fields.append('tests')
fields.append('lexer_test')
testdir = os.path.sep.join(fields)


def dirpath(*parts, **kwarg):
    dir = epwdir

    if kwarg.has_key('root'):
        dir = kwarg['root']
    else:
        dir = epwdir
    for part in parts:
        dir = dir + os.path.sep + part
    return dir


def filepath(filename, *parts, **kwarg):
    dir = dirpath(*parts, **kwarg)
    return dir + os.path.sep + filename


protodir = dirpath('prototype')
testdir = dirpath('tests')
srcdir = dirpath('src')

