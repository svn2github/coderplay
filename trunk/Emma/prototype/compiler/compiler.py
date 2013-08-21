from utils.utils import filepath, srcdir

opcode_string = \
'''
end

add
sub
mul
div
mod
pow
gt
ge
eq
le
lt
ne
and
or
xor

not
plus
minus

rot_two
rot_three

print
read

return
del

package
import

call

get_field
get_index
get_slice
get_idxlist

set_field
set_index
set_slice
set_idxlist

setup_for
for

hasarg

set_row

push
pushc
pushn
pop
funcdef
classdef
jump
fjump
tjump

mklist
mkhash

'''


def gen_c_code():
    opcodelist = ['OP_'+str.upper(t) for t in opcode_string.split('\n') if t != '']

    outs = open(filepath('opcode.hi', root=srcdir), 'w')
    for ii in range(len(opcodelist)):
        if opcodelist[ii] == 'OP_HASARG':
            outs.write('\n')
        outs.write('#define %-20s %d\n' % (opcodelist[ii], ii))
        if opcodelist[ii] == 'OP_HASARG':
            outs.write('\n')
    outs.write('\nextern char *opcode_types[];\n')
    outs.close()

    outs = open(filepath('opcode.i', root=srcdir), 'w')
    outs.write('char *opcode_types[] = {\n')
    outs.write('        "%s"' % opcodelist[0])
    for t in opcodelist[1:]:
        outs.write(',\n        "%s"' % t)
    outs.write('\n};\n')
    outs.close()


gen_c_code()


