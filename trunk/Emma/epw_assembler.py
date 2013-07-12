import sys
from epw_bytecode import *

''' Assemble the output from compiler into label less assembly code
'''

class CodeObject(object):

    def __init__(self, cp):
        self.name = cp.name
        self.parms = cp.parms
        self.kwParms = cp.kwParms
        self.constants = []
        self.varNames = []
        self.instrlist = []

    def __repr__(self, nindent=0):
        indent = '    '
        leading = indent * nindent
        out = leading + '--------------\n'
        out += leading + 'CodeObject: ' + self.name + '\n'
        out += leading + 'parms: ' + str(self.parms) + '\n'
        out += leading + 'kwParms: ' + str(self.kwParms) + '\n'
        out += leading + 'nConstants: ' + str(len(self.constants)) + '\n'
        out += leading + 'varNames: ' + str(self.varNames) + '\n'
        nlines = 0
        for instr in self.instrlist:
            lineno = '%-3d' % nlines
            if instr.opcode == OP_FUNCTION:
                out += leading + indent + lineno + opcode2str(instr.opcode) + '\n'
                out += self.constants[instr.args[0]].__repr__(nindent+2)
            else:
                out += leading + indent + lineno + opcode2str(instr.opcode)
                for arg in instr.args:
                    out += ' ' + str(arg)
                out += '\n'
            nlines += 1
        out += leading + '--------------\n'
        return out


def assemble(cp):

    co = CodeObject(cp)

    label_info = {}

    # first pass to collect labels, varnames and constants
    nlines = 0
    for instr in cp.instrlist:
        if instr.opcode == OP_LABEL:
            label = instr.args[0]
            label_info[label] = nlines
        else:
            if instr.opcode in [OP_PUSH, OP_POP]:
                varName = instr.args[0]
                if varName not in co.varNames:
                    co.varNames.append(varName)

            elif instr.opcode == OP_PUSHC:
                const = instr.args[0]
                if const not in co.constants:
                    co.constants.append(const)

            elif instr.opcode == OP_FUNCTION:
                funcCP = instr.args[0]
                funcDef = assemble(funcCP)
                if funcDef not in co.constants:
                    co.constants.append(funcDef)
                instr.args = (funcDef,)
            nlines += 1

    for instr in cp.instrlist:
        if instr.opcode != OP_LABEL:
            if instr.opcode in [OP_PUSH, OP_POP]:
                varName = instr.args[0]
                co.instrlist.append(Instruction(instr.opcode, co.varNames.index(varName)))
            elif instr.opcode == OP_PUSHC:
                const = instr.args[0]
                co.instrlist.append(Instruction(OP_PUSHC, co.constants.index(const)))
            elif instr.opcode == OP_FUNCTION:
                funcDef = instr.args[0]
                co.instrlist.append(Instruction(OP_FUNCTION, co.constants.index(funcDef)))
            elif instr.opcode in [OP_JUMP, OP_FJUMP]:
                label = instr.args[0]
                co.instrlist.append(Instruction(instr.opcode, label_info[label]))
            else:
                co.instrlist.append(instr)

    return co


