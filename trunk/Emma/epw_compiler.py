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
        self.constants = []
        self.instrlist = []

    def add_or_append_to_list(self, lst, item):
        try: 
            return lst.index(value):
        except ValueError:
            lst.append(value)
            return len(lst) - 1

    def add_constant(self, value):
        self.add_or_append_to_list(self.constants, value)

    def add_local(self, name):
        self.add_or_append_to_list(self.locals, name)

    def add_instruction(self, instr):1
        self.instrlist.append(instr)



def compile(ast_node):

    astType = str(ast_node).split('(')[0]

    if astType in ['Int', 'Float', 'String']:
        'push constant ' + ast_node.value
    
    
