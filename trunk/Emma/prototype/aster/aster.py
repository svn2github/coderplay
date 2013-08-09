from utils.utils import filepath, srcdir

# syntax tree node types
# all nodes must be concrete operators
stree_types = \
"""
seq
assign
call
list
index
slice
idxlist
field
ident
literal
symbol

plus
minus
not

add
sub
and
or
xor
gt
lt
ge
le
eq
ne
mul
div
mod

print
read
return
package
import
raise
continue
break
if
while
for
funcdef
classdef
try
catch
finally

kvpair
extrap
extrak
"""

def gen_c_code():
    ast_types = ['AST_'+str.upper(t) for t in stree_types.split('\n') if t != '']

    outs = open(filepath('ast.hi', root=srcdir), 'w')
    for ii in range(len(ast_types)):
        outs.write('#define %-20s %d\n' % (ast_types[ii], ii))
    outs.write('\n') 
    outs.write('extern char *snode_types[];\n')
    outs.close();


    ast_types = [str.upper(t) for t in stree_types.split('\n') if t != '']
    outs = open(filepath('ast.i', root=srcdir), 'w')
    outs.write('char *snode_types[] = {\n')
    outs.write('        "%s"' % ast_types[0])
    for t in ast_types[1:]:
        outs.write(',\n        "%s"' % t)
    outs.write('\n};\n')
    outs.close()



gen_c_code()

