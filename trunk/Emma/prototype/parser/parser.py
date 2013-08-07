from utils.utils import filepath, srcdir

# parse tree node types
ptree_types = \
"""
file_input
prompt_input
string_input
statement
simple_stmt
compound_stmt
expr
assign_stmt
print_stmt
read_stmt
continue_stmt
break_stmt
return_stmt
package_stmt
import_stmt
raise_stmt
target
trailer
if_stmt
while_stmt
for_stmt
funcdef
classdef
try_stmt
catch_stmt
finally_stmt
suite
stmt_block
for_expr
r_expr
r_term
r_factor
l_expr
a_expr
a_term
factor
power
primary
atom
expr_list
parmlist
oparm_list
oparm
kvpair
arglist
oarg
subscription
singleidx
idxrange
idxlist
"""

def gen_c_code():

    node_types = [str.upper(type) for type in ptree_types.split('\n') if type != '']

    outs = open(filepath('parser.hi', root=srcdir), 'w')
    for ii in range(len(node_types)):
        outs.write('#define %-20s %d\n' % (node_types[ii], ii+1000))
    outs.write('\n')
    for t in node_types:
        if t in ["FILE_INPUT", "PROMPT_INPUT", "STRING_INPUT"]:
            param = ''
        elif t in ['ASSIGN_STMT', 'KVPAIR']:
            param = 'Node *parent, Node *first'
        else:
            param = 'Node *parent'
        outs.write('Node *parse_%s(%s);\n' % (str.lower(t), param))
    outs.write('\nextern char *node_types[];\n')
    outs.close()

    outs = open(filepath('parser.i', root=srcdir), 'w')
    outs.write('\nchar *node_types[] = {\n')
    outs.write('        "%s"' % node_types[0])
    for t in node_types[1:]:
        outs.write(',\n        "%s"' % t)
    outs.write('\n};\n')
    outs.close()

gen_c_code()

