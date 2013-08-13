from utils.utils import filepath, srcdir

opcode_string = \
'''
stop
add
sub
mul
div
mod
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

hasarg

label

push
pushc
pop
func
call
return
jump
fjump
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

