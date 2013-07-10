import sys
from epw_bytecode import *
from epw_parser2 import *

''' Emma language compiler. 
    The results of compilation is the virtual machine code without line numbers.
    The line numbers will be generated in subsequent assembler phase.
'''

class ControlFlowGraph(object):

    def __init__(self):
        self.instrlist = []
        self.inspos_main = 0 # the position to insert a instruction
        self.pushpos_main = 0
        self.inspos_func = 0
        self.pushpos_func = 0
        self.label_counter = 0
        self.label_start = None
        self.label_end = None
        self.nindent = 0

    def __repr__(self):
        pass

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
            self.scope[name] = idx
            return idx


class Compiler(object):

    def __init__(self, symtab, cfg):
        self.symtab = symtab
        self.cfg = cfg
        self.label_counter = 0
        self.label_group = None

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
    

    def compile(self, parsed):
        label = parsed.label
        lst = parsed.lst

        if label == PN_LIST:
            for item in lst:
                compile(item)

        elif label == PN_IF:
            # get the labels
            _, label_end, label_false = self.make_label('IF')
            # the IF elements
            predicate, if_body = lst[0:2]
            # evaluate the predicate
            compile(predicate)
            self.insert_instruction(OP_FJUMP, label_false)
            compile(if_body)
            if len(lst) == 3: # we have an else body
                else_body = lst[2]
                self.insert_instruction(OP_JUMP, label_end)
                self.insert_instruction(OP_LABEL, label_false)
                compile(else_body)
                self.insert_instruction(OP_LABEL, label_end)
            else:
                self.insert_instruction(OP_LABEL, label_false)

        elif label == PN_WHILE:
            # get the labels
            label_start, label_end, _ = self.make_label('WHILE')
            # the while elements
            predicate, while_body = lst
            # predictate
            self.insert_instruction(OP_LABEL, label_start)
            compile(predicate)
            self.insert_instruction(OP_FJUMP, label_end)
            # loop
            compile(while_body)
            self.insert_instruction(OP_JUMP, label_start)
            self.insert_instruction(OP_LABEL, label_end)

        elif label == PN_FOR:
            # get the labels
            label_start, label_end, _ = self.make_label('FOR')
            # get the for elements
            counter, start, end, step, for_body = lst
            # save end to a temp location to avoid multi-evaluation
            compile(end) 
            self.insert_instruction(OP_POP, M_TEMP, 0)
            # save step to a temp location to avoid multi-evaluation
            compile(step) 
            self.insert_instruction(OP_POP, M_TEMP, 1)

            # assign start to counter
            compile(start) # start
            idx = self.symtab.get_or_set(counter.lst[0])
            self.insert_instruction(OP_POP, M_LOCAL, idx) 
            
            # where the for body starts
            self.insert_instruction(OP_LABEL, label_start)
            # compare counter to end
            self.insert_instruction(OP_PUSH, M_LOCAL, idx)
            self.insert_instruction(OP_PUSH, M_TEMP, 0)
            self.insert_instruction(OP_LE)
            # if counter is over the end, exit
            self.insert_instruction(OP_FJUMP, label_end)
            compile(for_body) # the loop body
            # loop increment
            self.insert_instruction(OP_PUSH, M_LOCAL, idx) 
            self.insert_instruction(OP_PUSH, M_TEMP, 1)
            self.insert_instruction(OP_ADD)
            self.insert_instruction(OP_POP, M_LOCAL, idx)
            self.insert_instruction(OP_JUMP, label_start) # goto start
            # the exit of the for struct
            self.insert_instruction(OP_LABEL, label_end)

        elif label == PN_DEF:
            # the function elements
            funcname, arglist, body = lst
            funcname = self.symtab.name + '$' + funcname.lst[0]
            # set the function definition in the current scope
            label = '(' + funcname + ')'
            self.push_instruction(OP_PUSH, M_CONSTANT, label)
            # save the function entry address to the func name var
            idx = self.symtab.get_or_set(funcname)
            self.push_instruction(OP_POP, M_LOCAL, idx) 

            # new symbol table for each function defined
            newSymtab = SymbolTable(funcname)
            newSymtab.parent = self.symtab
            # switch to the new symbol table for the function definition
            self.symtab = newSymtab
            # The function entry label
            self.insert_instruction(OP_LABEL, label)
            # the parameter list
            self.compile(arglist)
            # compile the body of the function
            self.compile(body)
            # get number of variables used in the function
            nVarsScope = self.symtab.nVarsScope
            # add the function nvars definition line
            self.insert_instruction(OP_FUNCTION, nVarsScope) 
            # restore the symbol table of main level
            self.symtab = self.symtab.parent

        elif label == PN_ARGLIST: # the function parameter list definition
            for item in lst:
                if item.label == PN_KWPARM:
                    parname, value = item.lst
                    idx = self.symtab.get_or_set(parname.lst[0])
                    compile(value)
                    cfg.push_instruction(OP_POP, M_LOCAL, idx)
                else:
                    parname = item
                    idx = self.symtab.get_or_set(parname.lst[0])

        elif label in [PN_INT, PN_FLOAT, PN_STRING]:
            idx = cfg.add_constant(lst[0])
            cfg.add_instruction(OP_PUSH, M_CONSTANT, idx)

        elif label == PN_VAR:
            varname = lst[0]
            idx = self.symtab.get_or_set(varname)
            cfg.insert_instruction(OP_PUSH, M_LOCAL, idx)

        elif label == PN_PAREN: # function call
            if lst[0].label == PN_VAR: # simple function
                segment, idx = cfg.lookup_name_in_segment(lst[0].lst[0])
                cfg.add_instruction(OP_PUSH, segment, idx)
            else: # complex function with ()[] chain
                compile(lst[0], cfg)

            # arglist
            nparms = 0
            nkws = 0
            for item in lst[1].lst:
                if item.label == PN_KWPARM:
                    cfg.add_call_kw(item.lst[0].lst[0]) # the keyword name is save in memory
                    compile(item.lst[1], cfg) # value left on stack
                    cfg.add_instruction(OP_POP, M_TEMP, 0)
                    nkws += 1
            for item in lst[1].lst:
                if item.label != PN_KWPARM:
                    compile(item, cfg)
                    nparms += 1
            idx = cfg.add_constant(nparms)
            cfg.add_instruction(OP_PUSH, M_CONSTANT, idx)
            idx = cfg.add_constant(nkws)
            cfg.add_instruction(OP_PUSH, M_CONSTANT, idx)
            cfg.add_instruction(OP_CALL)

        elif label == PN_CONTINUE:
            cfg.add_instruction(OP_JUMP, cfg.label_start)

        elif label == PN_BREAK:
            cfg.add_instruction(OP_JUMP, cfg.label_end)

        elif label == PN_RETURN:
            if len(lst) > 0:
                compile(lst[0])
            else:
                idx = cfg.add_constant(0)
                cfg.add_instruction(OP_PUSH, M_CONSTANT, idx)
            cfg.add_instruction(OP_RETURN)

        elif label == PN_BRACKET:
            if lst[0].label == PN_VAR: # simple array slice
                segment, idx = cfg.lookup_name_in_segment(lst[0].lst[0])
                cfg.add_instruction(OP_PUSH, segment, idx)
            else: # complex array slice with ()[] chain
                compile(lst[0], cfg)

            # idxlist
            nIdx = 0
            for item in lst[1].lst:
                compile(item, cfg)
                nIdx += 1

            cfg.add_instruction(OP_SLICE, nIdx)

        elif label == PN_PRINT:
            for item in lst:
                compile(item, cfg)
            cfg.add_instruction(OP_CALL, 'print', len(lst))

        elif label == PN_ASSIGN:
            compile(lst[1]) # the value
            if lst[0].label == PN_VAR: # simple variable
                segment, idx = cfg.lookup_name_in_segment(lst[0].lst[0])
                cfg.add_instruction(OP_POP, segment, idx)
            else: # any ()[] chain
                compile(lst[0].lst[0]) # the variable of function call
                compile(lst[0].lst[1]) # the slice TODO
                cfg.add_instruction(OP_POP, M_POINTER, 1) # pop pointer
                cfg.add_instruction(OP_POP, M_TEMP, 0)



        return cfg


