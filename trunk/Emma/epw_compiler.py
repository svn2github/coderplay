import sys
from epw_bytecode import *
from epw_parser2 import *

''' Emma language compiler. 
    The results of compilation is the virtual machine code without line numbers.
    The line numbers will be generated in subsequent assembler phase.
'''

class ControlFlowGraph(object):

    def __init__(self):
        self.instrlist = [Instruction(OP_STOP)]
        self.inspos_main = 0 # the position to insert a instruction
        self.pushpos_main = 0
        self.inspos_func = 1
        self.pushpos_func = 1
        self.label_counter = 0
        self.label_start = None
        self.label_end = None
        self.nindent = 0

    def __repr__(self):
        out = ''
        for instr in self.instrlist:
            out += opcode2str(instr.opcode)
            for arg in instr.args:
                out += ' ' + str(arg)
            out += '\n'
        return out

    def flatten(self):
        out = []
        for instr in self.instrlist:
            line = opcode2str(instr.opcode)
            for arg in instr.args:
                line += ' ' + str(arg)
            out.append(line)
        return out

    def insert_instruction_main(self, opcode, *args):
        self.instrlist.insert(self.inspos_main, Instruction(opcode, *args))
        self.inspos_main += 1
        self.pushpos_main += 1
        self.inspos_func += 1
        self.pushpos_func += 1

    def push_instruction_main(self, opcode, *args):
        ''' push an instruction at the end of the instruction list
            This is specifically for any function code. '''
        self.instrlist.insert(self.pushpos_main, Instruction(opcode, *args))
        self.pushpos_main += 1
        self.inspos_func += 1
        self.pushpos_func += 1

    def insert_instruction_func(self, opcode, *args):
        self.instrlist.insert(self.inspos_func, Instruction(opcode, *args))
        self.inspos_func += 1
        self.pushpos_func += 1

    def push_instruction_func(self, opcode, *args):
        ''' push an instruction at the end of the instruction list
            This is specifically for any function code. '''
        self.instrlist.insert(self.pushpos_func, Instruction(opcode, *args))
        self.pushpos_func += 1

    def make_label(self, prefix=''):
        label = self.name + '$' + prefix + str(self.label_counter)
        self.label_counter += 1
        return label

class SymbolTable(object):

    def __init__(self, name='$MAIN'):
        self.name = name
        self.scope = {}
        self.nVarsScope = 0
        self.parent = None

    def get_nVarsTotal(self):
        nVarsTotal = self.nVarsScope
        if self.parent:
            nVarsTotal += self.parent.get_nVarsTotal()
        return nVarsTotal

    def lookup_name(self, name):
        if self.scope.has_key(name):
            return self.scope[name]
        elif self.parent:
            return self.parent.lookup_name(name)
        else:
            return -1

    def get_or_set(self, name):
        idx = self.lookup_name(name)
        if idx >= 0: # get
            return idx
        else: # set
            idx = self.get_nVarsTotal()
            self.nVarsScope += 1
            self.scope[name] = idx
            return idx


class Compiler(object):

    def __init__(self):
        self.symtab = SymbolTable()
        self.cfg = ControlFlowGraph()
        self.label_counter = 0
        self.label_group = None

    def reset(self):
        self.symtab = SymbolTable()
        self.cfg = ControlFlowGraph()
        self.label_counter = 0
        self.label_group = None

    def reset_function_instruction(self):
        self.cfg.inspos_func = len(self.cfg.instrlist)
        self.cfg.pushpos_func = len(self.cfg.instrlist)

    def insert_instruction(self, opcode, *args):
        if self.symtab.name == '$MAIN':
            self.cfg.insert_instruction_main(opcode, *args)
        else:
            self.cfg.insert_instruction_func(opcode, *args)

    def push_instruction(self, opcode, *args):
        if self.symtab.name == '$MAIN':
            self.cfg.push_instruction_main(opcode, *args)
        else:
            self.cfg.push_instruction_func(opcode, *args)

    def make_label(self, prefix):
        prefix = self.symtab.name + '$' + prefix + '-'
        counter = str(self.label_counter)
        self.label_counter += 1
        self.label_group = prefix+'START'+counter, prefix+'END'+counter, prefix+'FALSE'+counter
        return self.label_group
    
    def set_new_symtab(self, newSymtab):
        newSymtab.parent = self.symtab
        # switch to the new symbol table for the function definition
        self.symtab = newSymtab

    def restore_symtab(self):
        self.symtab = self.symtab.parent

    def compile(self, parsed):
        label = parsed.label
        lst = parsed.lst

        if label == PN_LIST:
            for item in lst:
                self.compile(item)

        elif label == PN_IF:
            # get the labels
            _, label_end, label_false = self.make_label('IF')
            # the IF elements
            predicate, if_body = lst[0:2]
            # evaluate the predicate
            self.compile(predicate)
            self.push_instruction(OP_FJUMP, label_false)
            self.compile(if_body)
            if len(lst) == 3: # we have an else body
                else_body = lst[2]
                self.push_instruction(OP_JUMP, label_end)
                self.push_instruction(OP_LABEL, label_false)
                self.compile(else_body)
                self.push_instruction(OP_LABEL, label_end)
            else:
                self.push_instruction(OP_LABEL, label_false)

        elif label == PN_WHILE:
            # get the labels
            label_start, label_end, _ = self.make_label('WHILE')
            # the while elements
            predicate, while_body = lst
            # predictate
            self.push_instruction(OP_LABEL, label_start)
            self.compile(predicate)
            self.push_instruction(OP_FJUMP, label_end)
            # loop
            self.compile(while_body)
            self.push_instruction(OP_JUMP, label_start)
            self.push_instruction(OP_LABEL, label_end)

        elif label == PN_FOR:
            # get the labels
            label_start, label_end, _ = self.make_label('FOR')
            # get the for elements
            counter, start, end, step, for_body = lst
            # save end to a temp location to avoid multi-evaluation
            self.compile(end) 
            self.push_instruction(OP_POP, M_TEMP, 0)
            # save step to a temp location to avoid multi-evaluation
            self.compile(step) 
            self.push_instruction(OP_POP, M_TEMP, 1)

            # assign start to counter
            self.compile(start) # start
            idx = self.symtab.get_or_set(counter.lst[0])
            self.push_instruction(OP_POP, M_LOCAL, idx) 
            
            # where the for body starts
            self.push_instruction(OP_LABEL, label_start)
            # compare counter to end
            self.push_instruction(OP_PUSH, M_LOCAL, idx)
            self.push_instruction(OP_PUSH, M_TEMP, 0)
            self.push_instruction(OP_LE)
            # if counter is over the end, exit
            self.push_instruction(OP_FJUMP, label_end)
            self.compile(for_body) # the loop body
            # loop increment
            self.push_instruction(OP_PUSH, M_LOCAL, idx) 
            self.push_instruction(OP_PUSH, M_TEMP, 1)
            self.push_instruction(OP_ADD)
            self.push_instruction(OP_POP, M_LOCAL, idx)
            self.push_instruction(OP_JUMP, label_start) # goto start
            # the exit of the for struct
            self.push_instruction(OP_LABEL, label_end)

        elif label == PN_DEF:
            # the function elements
            funcname, arglist, body = lst
            funcname = funcname.lst[0]
            # set the function definition in the current scope
            label = '(' + funcname + ')'
            self.push_instruction(OP_PUSH, M_CONSTANT, label)
            # save the function entry address to the func name var
            idx = self.symtab.get_or_set(funcname)
            self.push_instruction(OP_POP, M_LOCAL, idx) 

            # new symbol table for each function defined
            self.set_new_symtab(SymbolTable(funcname))
            # initialize the function instruction insert and push position
            self.reset_function_instruction()

            # The function entry label
            self.insert_instruction(OP_LABEL, label)
            # the parameter list
            self.compile(arglist)
            # compile the body of the function
            self.compile(body)
            # get number of variables used in the function
            nVarsScope = self.symtab.nVarsScope
            # insert the function nvars definition line
            self.insert_instruction(OP_FUNCTION, funcname, nVarsScope) 
            # restore the symbol table of main level
            self.restore_symtab()

        elif label == PN_ARGLIST: # the function parameter list definition
            nkws = 0
            nparms = 0
            for item in lst:
                if item.label == PN_KWPARM:
                    parname, value = item.lst
                    parname = parname.lst[0]
                    idx = self.symtab.get_or_set(parname)
                    self.push_instruction(OP_PUSH, M_CONSTANT, parname)
                    self.compile(value)
                    self.push_instruction(OP_MAKEKW) # make a kw obj on the stack
                    self.push_instruction(OP_POP, M_LOCAL, idx) # save to local segment
                    nkws += 1
            for item in lst:
                if item.label != PN_KWPARM:
                    parname = item.lst[0]
                    idx = self.symtab.get_or_set(parname)
                    self.push_instruction(OP_PUSH, M_CONSTANT, 0)
                    self.push_instruction(OP_POP, M_LOCAL, idx)
                    nparms += 1
            self.push_instruction(OP_PUSH, M_CONSTANT, nparms)
            self.push_instruction(OP_PUSH, M_CONSTANT, nkws)

        elif label in [PN_INT, PN_FLOAT, PN_STRING]:
            value = lst[0]
            self.push_instruction(OP_PUSH, M_CONSTANT, value)

        elif label == PN_VAR:
            varname = lst[0]
            idx = self.symtab.get_or_set(varname)
            self.push_instruction(OP_PUSH, M_LOCAL, idx)

        elif label == PN_PAREN: # function call

            self.compile(lst[0]) # should leave the function on top of stack

            # arglist
            nparms = 0
            nkws = 0
            for item in lst[1].lst:
                if item.label == PN_KWPARM:
                    parname, value = item.lst
                    parname = parname.lst[0]
                    self.push_instruction(OP_PUSH, M_CONSTANT, parname)
                    self.compile(value)
                    self.push_instruction(OP_MAKEKW)
                    self.push_instruction(OP_POP, M_ARG, nkws)
                    nkws += 1
            for item in lst[1].lst:
                if item.label != PN_KWPARM:
                    self.compile(item)
                    self.push_instruction(OP_POP, M_ARG, nparms+nkws)
                    nparms += 1
            
            self.push_instruction(OP_PUSH, M_CONSTANT, nparms)
            self.push_instruction(OP_PUSH, M_CONSTANT, nkws)
            self.push_instruction(OP_CALL)

        elif label == PN_CONTINUE:
            self.push_instruction(OP_JUMP, self.label_group[0])

        elif label == PN_BREAK:
            cfg.add_instruction(OP_JUMP, self.label_group[1])

        elif label == PN_RETURN:
            if len(lst) > 0:
                self.compile(lst[0])
            else:
                self.push_instruction(OP_PUSH, M_CONSTANT, 0)
            self.push_instruction(OP_RETURN)

        elif label == PN_BRACKET:
            self.compile(lst[0]) # this should leave the array on the top of stack

            # PN_IDXLIST
            nIdx = 0
            for item in lst[1].lst:
                self.compile(item)
                nIdx += 1

            self.push_instruction(OP_SLICE, nIdx) # create an array slice object

        elif label == PN_PRINT:
            for item in lst:
                self.compile(item)
            self.push_instruction(OP_PUSH, M_CONSTANT, len(lst)) # nargs
            self.push_instruction(OP_PUSH, M_CONSTANT, 0) # nkws
            self.push_instruction(OP_CALL, 'print')

        elif label == PN_ASSIGN:
            if lst[0].label == PN_VAR: # simple varialbe
                name = lst[0].lst[0]
                idx = self.symtab.get_or_set(name)
                self.compile(lst[1])
                self.push_instruction(OP_POP, M_LOCAL, idx)
            else:
                self.compile(lst[0]) # the variable to be assigned
                self.push_instruction(OP_POP, M_POINTER, 1)
                self.compile(lst[1]) # the value
                self.push_instruction(OP_POP, M_THAT, 0)

        elif label == PN_BINOP:
            lhs, op, rhs = lst
            self.compile(lhs)
            self.compile(rhs)
            if op == '+': 
                self.push_instruction(OP_ADD)
            elif op == '-':
                self.push_instruction(OP_SUB)
            elif op == '*':
                self.push_instruction(OP_MUL)
            elif op == '/':
                self.push_instruction(OP_DIV)
            elif op == '%':
                self.push_instruction(OP_MOD)
            elif op == '>':
                self.push_instruction(OP_GT)
            elif op == '>=':
                self.push_instruction(OP_GE)
            elif op == '==':
                self.push_instruction(OP_EQ)
            elif op == '<=':
                self.push_instruction(OP_LE)
            elif op == '<':
                self.push_instruction(OP_LT)
            elif op == '!=':
                self.push_instruction(OP_NE)
            elif op == 'and':
                self.push_instruction(OP_AND)
            elif op == 'or':
                self.push_instruction(OP_OR)
            elif op == 'xor':
                self.push_instruction(OP_XOR)

        elif label == PN_UNARYOP:
            op, operand = lst
            self.compile(operand)
            if op == '-':
                self.push_instruction(OP_NEG)
            elif op == 'not':
                self.push_instruction(OP_NOT)

        elif label == PN_NONE:
            self.push_instruction(OP_PUSH, M_CONSTANT, None)


        return self.cfg.flatten()


