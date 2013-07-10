import sys
from epw_bytecode import *
from epw_parser2 import *

''' Emma language compiler. 
    The results of compilation is the virtual machine code without line numbers.
    The line numbers will be generated in subsequent assembler phase.
'''

class ControlFlowGraph(object):

    def __init__(self):
        self.name = 'null'
        self.symtab = {}
        self.args = []
        # Each element save the address where the value of this 
        # local variable is stored in the main heap.
        self.locals = [] 
        self.constants = []
        self.funcdefs = []
        self.call_kws = []
        self.instrlist = []
        self.label_counter = 0
        self.label_start = None
        self.label_end = None
        self.nindent = 0

    def __repr__(self):
        leading = '  ' * self.nindent
        out = leading + '-----------\n'
        out += leading + 'function: ' + self.name + '\n'
        out += leading + 'args: ' + str(self.args) + '\n'
        out += leading + 'locals: ' + str(self.locals) + '\n'
        out += leading + 'constants: ' + str(self.constants) + '\n'
        out += leading + 'call_kws: ' + str(self.call_kws) + '\n'
        out += leading + 'nfuncdefs: ' + str(len(self.funcdefs)) + '\n'

        for instr in self.instrlist:
            if instr.opcode == OP_FUNCTION:
                out += leading + opcode2str(instr.opcode) 
                out += ' ' + str(instr.args[0]) + '\n'
                self.nindent += 1
                self.funcdefs[instr.args[0]].nindent = self.nindent + 1
                out += leading + str(self.funcdefs[instr.args[0]])
                self.nindent -= 1
            else:
                out += leading + opcode2str(instr.opcode)
                for arg in instr.args:
                    out += ' ' + str(arg)
                out += '\n'

        out += leading + '-----------\n'
        return out


    def add_or_append_to_list(self, lst, item):
        try: 
            return lst.index(item)
        except ValueError:
            lst.append(item)
            return len(lst) - 1

    def add_symbol(self, symbol):
        if self.symtab.has_key(symbol):
            return self.symtab[symbol]
        else:
            self.symtab[symbol] = self.len(self.locals)
            self.locals.append(None)
            return self.symtab[symbol]

    def add_constant(self, value):
        return self.add_or_append_to_list(self.constants, value)

    def add_arg(self, name):
        return self.add_or_append_to_list(self.args, name)

    def add_local(self, name):
        return self.add_or_append_to_list(self.locals, name)

    def add_funcdef(self, name):
        return self.add_or_append_to_list(self.funcdefs, name)

    def add_call_kw(self, name):
        return self.add_or_append_to_list(self.call_kws, name)

    def set_segment_content(self, segment, index, value):
        if segment == M_CONSTANT:
            self.constants[index] = value
        elif segment == M_ARG:
            self.args[index] = value
        elif segment == M_LOCAL:
            self.locals[index] = value

    def lookup_name_in_segment(self, name):
        if name in self.args:
            return M_ARG, self.args.index(name)
        elif name in self.locals:
            return M_LOCAL, self.locals.index(name)
        else:
            print 'not name found ' + name

    def add_instruction(self, opcode, *args):
        self.instrlist.append(Instruction(opcode, *args))

    def make_label(self, prefix=''):
        label = self.name + '$' + prefix + str(self.label_counter)
        self.label_counter += 1
        return label


def compile(parsed, cfg, segment=M_LOCAL):

    label = parsed.label
    lst = parsed.lst

    if label == PN_LIST:
        for item in lst:
            compile(item, cfg)

    elif label == PN_IF:
        label_false = cfg.make_label('IF-FALSE')
        label_end = cfg.make_label('IF-END')
        predicate, if_body = lst[0:2]
        # evaluate the predicate
        compile(predicate, cfg)
        cfg.add_instruction(OP_FJUMP, label_false)
        compile(if_body, cfg)
        if len(lst) == 3: # we have an else body
            else_body = lst[2]
            cfg.add_instruction(OP_JUMP, label_end)
            cfg.add_instruction(OP_LABEL, label_false)
            compile(else_body, cfg)
            cfg.add_instruction(OP_LABEL, label_end)
        else:
            cfg.add_instruction(OP_LABEL, label_false)

    elif label == PN_WHILE:
        label_start = cfg.make_label('WHILE-START')
        label_end = cfg.make_label('WHILE-FALSE')
        cfg.label_start = label_start
        cfg.label_end = label_end

        predicate, while_body = lst
        # predictate
        cfg.add_instruction(OP_LABEL, label_start)
        compile(predicate, cfg)
        cfg.add_instruction(OP_FJUMP, label_end)
        # loop
        compile(while_body, cfg)
        cfg.add_instruction(OP_JUMP, label_start)
        cfg.add_instruction(OP_LABEL, label_end)

    elif label == PN_FOR:
        label_start = cfg.make_label('FOR-START')
        label_end = cfg.make_label('FOR-END')
        cfg.label_start = label_start
        cfg.label_end = label_end

        counter, start, end, step, for_body = lst

        compile(end, cfg) # end
        cfg.add_instruction(OP_POP, M_TEMP, 0)
        compile(step, cfg) # step
        cfg.add_instruction(OP_POP, M_TEMP, 1)

        # assign start to counter
        compile(start, cfg) # start
        segment, idx = compile(counter, cfg) # the counter
        cfg.add_instruction(OP_POP, segment, idx) 
        
        # where the for struct starts
        cfg.add_instruction(OP_LABEL, label_start)
        # compare counter to end
        cfg.add_instruction(OP_PUSH, segment, idx)
        cfg.add_instruction(OP_PUSH, M_TEMP, 0)
        cfg.add_instruction(OP_LE)

        cfg.add_instruction(OP_FJUMP, label_end)
        compile(for_body, cfg) # the loop body

        cfg.add_instruction(OP_PUSH, segment, idx) # loop increment
        cfg.add_instruction(OP_PUSH, M_TEMP, 1)
        cfg.add_instruction(OP_ADD)
        cfg.add_instruction(OP_POP, segment, idx)
        cfg.add_instruction(OP_JUMP, label_start) # goto start

        cfg.add_instruction(OP_LABEL, label_end)

    elif label == PN_DEF:
        funcname, arglist, body = lst
        compile(funcname, cfg) # function name
        sub_cfg = ControlFlowGraph()
        sub_cfg.name = funcname.lst[0]
        compile(lst[1], sub_cfg, M_ARG) # arglist
        compile(lst[2], sub_cfg) # body
        idx = cfg.add_funcdef(sub_cfg)  # let the CFG save the funcdef at compile time
        # The op code will assign the function def to the variable at runtime
        cfg.add_instruction(OP_FUNCTION, idx) 

    elif label == PN_ARGLIST: # the function parameter list definition
        for item in lst:
            if item.label == PN_KWPARM:
                parname, value = item.list
                compile(parname, cfg)
                cfg.add_instruction(OP_POP, M_POINTER, 1)
                compile(value, cfg)
                cfg.add_instruction(OP_POP, THAT, 0)
            else:
                compile(item, cfg)

    elif label in [PN_INT, PN_FLOAT, PN_STRING]:
        idx = cfg.add_constant(lst[0])
        cfg.add_instruction(OP_PUSH, M_CONSTANT, idx)

    elif label == PN_VAR:
        varname = lst[0]
        idx = cfg.add_symbol(varname)
        cfg.add_instruction(OP_PUSH, M_LOCAL, idx)

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


