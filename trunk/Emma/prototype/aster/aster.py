from utils.utils import filepath, srcdir

# syntax tree node types
# all nodes must be concrete operators
stree_types = \
"""
seq
assign
expr
binop
unaryop
call
list
sub
slice
slist
field
ident
int
float
str
nul

print
read
continue
break
return
package
import
raise
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

    outs.close();





gen_c_code()

