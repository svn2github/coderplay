
''' Bytecode class for Emma language.
'''

OP_PUSH     = 0
OP_POP      = 1
OP_LABEL    = 2
OP_JUMP     = 3
OP_FJUMP    = 4
OP_FUNCTION = 5
OP_RETURN   = 6
OP_CALL     = 7
OP_ADD      = 8
OP_SUB      = 9
OP_MUL      = 10
OP_DIV      = 11
OP_MOD      = 12
OP_GT       = 13
OP_GE       = 14
OP_EQ       = 15
OP_LE       = 16
OP_LT       = 17
OP_NE       = 18
OP_AND      = 19
OP_OR       = 20
OP_XOR      = 21
OP_NOT      = 22
OP_NEG      = 23

OP_SLICE    = 24

opcode_dict = {}
opcode_dict[OP_PUSH] = 'push'
opcode_dict[OP_POP] = 'pop'
opcode_dict[OP_LABEL] = 'label'
opcode_dict[OP_JUMP] = 'jump'
opcode_dict[OP_FJUMP] = 'fjump'
opcode_dict[OP_FUNCTION] = 'function'
opcode_dict[OP_RETURN] = 'return'
opcode_dict[OP_CALL] = 'call'
opcode_dict[OP_ADD] = 'add'
opcode_dict[OP_SUB] = 'sub'
opcode_dict[OP_MUL] = 'mul'
opcode_dict[OP_DIV] = 'div'
opcode_dict[OP_MOD] = 'mod'
opcode_dict[OP_GT] = 'gt'
opcode_dict[OP_GE] = 'ge'
opcode_dict[OP_EQ] = 'eq'
opcode_dict[OP_LE] = 'le'
opcode_dict[OP_LT] = 'lt'
opcode_dict[OP_LE] = 'le'
opcode_dict[OP_NE] = 'ne'
opcode_dict[OP_AND] = 'and'
opcode_dict[OP_OR] = 'or'
opcode_dict[OP_XOR] = 'xor'
opcode_dict[OP_NOT] = 'not'
opcode_dict[OP_NEG] = 'neg'

opcode_dict[OP_SLICE] = 'slc'

def opcode2str(opcode):
    return opcode_dict[opcode]

M_CONSTANT      = 'constant'
M_LOCAL         = 'local'
M_ARG           = 'argument'
M_TEMP          = 'temp'
M_POINTER       = 'pointer'
M_THIS          = 'this'
M_THAT          = 'that'


class Instruction(object):

    def __init__(self, opcode, *args):
        self.opcode = opcode
        self.args = args



