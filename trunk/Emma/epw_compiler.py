import sys
from epw_bytecode import *
from epw_parser2 import *

''' Emma language compiler. 
    The results of compilation is the virtual machine code without line numbers.
    The line numbers will be generated in subsequent assembler phase.
'''

class CompiledProc(object):

    def __init__(self, name='$MAIN$'):
        self.name = name
        self.parms = []
        self.kwParms = []
        self.instrlist = []
        self.parent = None

    def __repr__(self, nindent=0):
        indent = '    '
        leading = indent * nindent
        out = leading + '--------------\n'
        out += leading + 'CP: ' + self.name + '\n'
        out += leading + 'parms: ' + str(self.parms) + '\n'
        out += leading + 'kwParms' + str(self.kwParms) + '\n'
        for instr in self.instrlist:
            if instr.opcode == OP_FUNCTION:
                out += leading + indent + opcode2str(instr.opcode) + '\n'
                out += instr.args[0].__repr__(nindent+2)
            else:
                out += leading + indent + opcode2str(instr.opcode)
                for arg in instr.args:
                    out += ' ' + str(arg)
                out += '\n'
        out += leading + '--------------\n'
        return out


class Compiler(object):

    def __init__(self):
        self.CP = CompiledProc()
        self.label_counter = 0
        self.label_continue = []
        self.label_break = []
        self.tempvar_counter = 0

    def switchNewCP(self, funcName):
        newCP = CompiledProc(funcName)
        newCP.parent = self.CP
        self.CP = newCP

    def restoreCP(self):
        self.CP = self.CP.parent

    def add_parm(self, parmName):
        self.CP.parms.append(parmName)

    def add_kwParm(self, kwParmName):
        self.CP.kwParms.append(kwParmName)

    def add_instruction(self, opcode, *args):
        self.CP.instrlist.append(Instruction(opcode, *args))

    def make_label(self, prefix):
        prefix = self.CP.name + '$' + prefix + '-'
        counter = str(self.label_counter)
        self.label_counter += 1
        return prefix+'START'+counter, prefix+'END'+counter, prefix+'FALSE'+counter

    def make_temp_varname(self):
        tempvarname = self.CP.name + 'tmp' + str(self.tempvar_counter)
        self.tempvar_counter += 1
        return tempvarname

    def compile(self, parsed):
        self._compile(parsed)
        CP = self.CP
        self.CP = CompiledProc()
        return CP

    def _compile(self, parsed):
        label = parsed.label
        lst = parsed.lst

        if label == PN_LIST:
            for item in lst:
                self._compile(item)

        elif label == PN_IF:
            # get the labels
            _, label_end, label_false = self.make_label('IF')
            # the IF elements
            predicate, if_body = lst[0:2]
            # evaluate the predicate
            self._compile(predicate)
            self.add_instruction(OP_FJUMP, label_false)
            self._compile(if_body)
            if len(lst) == 3: # we have an else body
                else_body = lst[2]
                self.add_instruction(OP_JUMP, label_end)
                self.add_instruction(OP_LABEL, label_false)
                self._compile(else_body)
                self.add_instruction(OP_LABEL, label_end)
            else:
                self.add_instruction(OP_LABEL, label_false)

        elif label == PN_WHILE:
            # get the labels
            label_start, label_end, _ = self.make_label('WHILE')
            # add to label management
            self.label_continue.append(label_start)
            self.label_break.append(label_end)
            # the while elements
            predicate, while_body = lst
            # predictate
            self.add_instruction(OP_LABEL, label_start)
            self._compile(predicate)
            self.add_instruction(OP_FJUMP, label_end)
            # loop
            self._compile(while_body)
            self.add_instruction(OP_JUMP, label_start)
            self.add_instruction(OP_LABEL, label_end)
            # remove labels from management
            self.label_continue.pop()
            self.label_break.pop()

        elif label == PN_FOR:
            # get the labels
            label_start, label_end, _ = self.make_label('FOR')
            # add to label management
            self.label_continue.append(label_start)
            self.label_break.append(label_end)
            # get the for elements
            counter, start, end, step, for_body = lst
            # save end to a temp location to avoid multi-evaluation
            self._compile(end) 
            endvarname = self.make_temp_varname()
            self.add_instruction(OP_POP, endvarname)
            # save step to a temp location to avoid multi-evaluation
            self._compile(step) 
            stepvarname = self.make_temp_varname()
            self.add_instruction(OP_POP, stepvarname)

            # assign start to counter
            self._compile(start) # start
            self.add_instruction(OP_PUSHC, 1)
            self.add_instruction(OP_SUB) # pre-decrement the counter
            counterName = counter.lst[0]
            self.add_instruction(OP_POP, counterName)

            # where the for body starts
            self.add_instruction(OP_LABEL, label_start)

            # loop increment
            self.add_instruction(OP_PUSH, counterName)
            self.add_instruction(OP_PUSHC, 1)
            self.add_instruction(OP_ADD)
            self.add_instruction(OP_POP, counterName)
            
            # compare counter to end
            self.add_instruction(OP_PUSH, counterName) 
            self.add_instruction(OP_PUSH, endvarname)
            self.add_instruction(OP_LE)
            # if counter is over the end, exit
            self.add_instruction(OP_FJUMP, label_end)
            # the loop body
            self._compile(for_body) 
            # goto start
            self.add_instruction(OP_JUMP, label_start) 
            # the exit of the for struct
            self.add_instruction(OP_LABEL, label_end)
            # remove labels from management
            self.label_continue.pop()
            self.label_break.pop()

        elif label == PN_DEF:
            # the function elements
            funcName, arglist, body = lst
            funcName = funcName.lst[0]
            # starting a new compiled proc
            self.switchNewCP(funcName)

            # the parameter list
            self._compile(arglist)
            # recursively compile the body of the function
            self._compile(body)

            # save the function's CP before restore
            funcCP = self.CP
            # restore compiled proc to main
            self.restoreCP()

            # any function w/o return will return a 0 by default
            if len(funcCP.instrlist)==0 or funcCP.instrlist[-1].opcode != OP_RETURN:
                funcCP.instrlist.append(Instruction(OP_PUSHC, 0))
                funcCP.instrlist.append(Instruction(OP_RETURN))

            # let the main proc know that we are having a new func CP
            self.add_instruction(OP_FUNCTION, funcCP)
            # associate the definition to the varname
            self.add_instruction(OP_POP, funcName)

        elif label == PN_ARGLIST: # the function parameter list definition
            for item in lst: # position parameter
                if item.label != PN_KWPARM:
                    parmName = item.lst[0]
                    self.add_parm(parmName)

            n = 0
            for item in lst: # keyword parameter
                if item.label == PN_KWPARM:
                    parmName, value = item.lst
                    parmName = parmName.lst[0]
                    self.add_kwParm(parmName)
                    # following code calculates the default value for the keyword
                    # parameter and tells the VM to load the value into the running
                    # Enviroment for the kw parm name.
                    self._compile(value)
                    self.add_instruction(OP_KWPARM, n)
                    n += 1

        elif label in [PN_INT, PN_FLOAT, PN_STRING]:
            value = lst[0]
            self.add_instruction(OP_PUSHC, value)

        elif label == PN_VAR:
            varname = lst[0]
            self.add_instruction(OP_PUSH, varname)

        elif label == PN_PAREN: # function call

            # arglist
            for item in lst[1].lst: # position arguments
                if item.label != PN_KWPARM:
                    self._compile(item)
            for item in lst[1].lst: # keyword arguments
                if item.label == PN_KWPARM:
                    argName, value = item.lst
                    argName = argName.lst[0]
                    self.add_instruction(OP_PUSHC, argName)
                    self._compile(value)
                    # make a keyword argument onto stack
                    self.add_instruction(OP_KWARG) 

            # Put the function on top of stack
            self._compile(lst[0]) 
            self.add_instruction(OP_CALL, len(lst[1].lst))

        elif label == PN_CONTINUE:
            self.add_instruction(OP_JUMP, self.label_continue[-1])

        elif label == PN_BREAK:
            self.add_instruction(OP_JUMP, self.label_break[-1])

        elif label == PN_RETURN:
            if len(lst) > 0:
                self._compile(lst[0])
            else:
                self.add_instruction(OP_PUSHC, 0)
            self.add_instruction(OP_RETURN)

        elif label == PN_BRACKET: # array slices
            # push the array like thingy on the top of stack
            self._compile(lst[0]) 

            # PN_IDXLIST
            nIdx = 0
            for item in lst[1].lst:
                self._compile(item)
                nIdx += 1

            # create an array slice object on top of the stack
            self.add_instruction(OP_SLICE, nIdx) 

        elif label == PN_PRINT:
            for item in lst:
                self._compile(item)
            self.add_instruction(OP_PUSH, 'print')
            self.add_instruction(OP_CALL, len(lst))

        elif label == PN_ASSIGN:
            if lst[0].label == PN_VAR: # simple variable
                self._compile(lst[1]) # value
                self.add_instruction(OP_POP, lst[0].lst[0])
            else:
                self._compile(lst[0]) # the variable to be assigned
                self._compile(lst[1]) # the value
                self.add_instruction(OP_PUSH, 'assign')
                self.add_instruction(OP_CALL, 2)

        elif label == PN_BINOP:
            lhs, op, rhs = lst
            self._compile(lhs)
            self._compile(rhs)
            if op == '+': 
                self.add_instruction(OP_ADD)
            elif op == '-':
                self.add_instruction(OP_SUB)
            elif op == '*':
                self.add_instruction(OP_MUL)
            elif op == '/':
                self.add_instruction(OP_DIV)
            elif op == '%':
                self.add_instruction(OP_MOD)
            elif op == '>':
                self.add_instruction(OP_GT)
            elif op == '>=':
                self.add_instruction(OP_GE)
            elif op == '==':
                self.add_instruction(OP_EQ)
            elif op == '<=':
                self.add_instruction(OP_LE)
            elif op == '<':
                self.add_instruction(OP_LT)
            elif op == '!=':
                self.add_instruction(OP_NE)
            elif op == 'and':
                self.add_instruction(OP_AND)
            elif op == 'or':
                self.add_instruction(OP_OR)
            elif op == 'xor':
                self.add_instruction(OP_XOR)

        elif label == PN_UNARYOP:
            op, operand = lst
            self._compile(operand)
            if op == '-':
                self.add_instruction(OP_NEG)
            elif op == 'not':
                self.add_instruction(OP_NOT)

        elif label == PN_NONE:
            self.add_instruction(OP_PUSHC, None)

