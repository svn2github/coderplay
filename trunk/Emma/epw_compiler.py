import sys
from epw_bytecode import *

''' Driver of Emma language compiler. 
    The results of compilation is the virtual machine code without line numbers.
    The line numbers will be generated in subsequent assembler phase.
'''

class ControlFlowGraph(object):

    def __init__(self):
        self.args = []
        self.locals = []
        self.instrlist = []

    def addInstruction(self, instr):
        self.instrlist.append(instr)

            


def compile(ast_node):

    astType = str(ast_node).split('(')[0]

    if astType in ['Int', 'Float', 'String']:
        'push constant ' + ast_node.value
    
    
