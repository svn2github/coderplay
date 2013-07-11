import sys
from epw_bytecode import *

''' The Virtual Machine.

'''

class CollectionSlice(object):

    def __init__(self, collection, *idxlist):
        self.collection = collection
        self.idxlist = idxlist


class make_instruction(object):

    def __init__(self, line):
        fields = line.split()
        self.opcode = fields[0]
        self.args = fields[1:]


class VM(object):

    def __init__(self):
        # The memory segments
        self.local = [] 
        self.argument = []
        self.temp = []
        self.pointer = []
        self.this = []
        self.that = []
        # The current base of memory segments 
        self.LCL = 0
        self.ARG = 0
        # the working stack
        self.stack = []
        # frame stack
        self.frameStack = []
        # program counter
        self.PC = 0


    def safe_get_segment_index(self, segment, index):
        if index < len(segment) and index >= 0:
            return segment[index]
        else:
            raise RuntimeError('Out of segment boundary')


    def get_segment_index(self, segment, index):
        if segment == M_ARG:
            return self.safe_get_segment_index(self.argument, index)

        elif segment == M_LOCAL:
            return self.safe_get_segment_index(self.local, index)

        elif segment == M_POINTER:
            return self.safe_get_segment_index(self.pointer, index)

        elif segment == M_THIS:
            return self.this[index]

        elif segment == M_THAT:
            if isinstance(self.pointer[1], CollectionSlice):
                collection = self.pointer[1].collection
                idxlist = self.pointer[1].idxlist
                if len(idxlist) == 1:
                    return collection[idxlist[0]]
                else:
                    return collection[slice(idxlist)]
            else:
                raise RuntimeError('Pointer 1 is not a CollectionSlice object')


    def safe_set_segment_index(self, segment, index, value):
        if index < len(segment) and index >= 0:
            segment[index] = value
        elif index == len(segment):
            segment.append(value)
        else:
            raise RuntimeError('Out of segment boundary')


    def set_segment_index(self, segment, index, value):
        if segment == M_ARG:
            self.safe_set_segment_index(self.argument, index, value)

        elif segment == M_LOCAL:
            self.safe_set_segment_index(self.local, index, value)

        elif segment == M_POINTER:
            self.safe_set_segment_index(self.pointer, index, value)

        elif segment == M_THIS:
            self.safe_set_segment_index(self.this, index, value)

        elif segment == M_THAT:
            if isinstance(self.pointer[1], CollectionSlice):
                collection = self.pointer[1].collection
                idxlist = self.pointer[1].idxlist
                if len(idxlist) == 1:
                    collection[idxlist[0]] = value
                else:
                    collection[slice(idxlist)] = value
            else:
                raise RuntimeError('Pointer 1 is not a CollectionSlice object')


    def run(self, instrlist):

        while self.PC < len(instrlist):

            instr = make_instruction(instrlist[self.PC])

            opcode = str2opcode(instr.opcode)

            if opcode == OP_PUSH:
                segment, index = instr.args
                if segment == M_CONSTANT:
                    if index.startswith('str='):
                        index = index[4:]
                    else:
                        index = int(index)
                    self.stack.append(index)
                else:
                    self.stack.append(self.get_segment_index(segment, int(index)))

            elif opcode == OP_POP:
                segment, index = instr.args
                value = self.stack.pop()
                self.set_segment_index(segment, int(index), value)

            elif opcode == OP_JUMP:
                self.PC = instr.args[0]
                continue

            elif opcode == OP_FJUMP:
                value = self.stack.pop()
                if not value:
                    self.PC = instr.args[0]
                    continue

            elif opcode == OP_FUNCTION: # function funcName nlocals
                # number of passed arguments and kws
                nkws = self.stack.pop()
                nargs = self.stack.pop()
                arglist = []
                for i in range(nargs):
                    arglist.append(self.stack.pop())
                kwlist = []
                for i in range(nkws):
                    kwlist.append(self.stack.pop())

                nlocals = instr.args[1]
                for ii in range(nlocals):
                    self.stack.append(None)

            elif opcode == OP_RETURN:
                pass

            elif opcode == OP_CALL: # call
                func = self.stack.pop()
                if type(func) == str: # built-in function
                    funcName = func
                    if funcName == 'print':
                        builtin_print(self.stack)
                    else:
                        pass
                else: # user-defined function address
                    funcAddress = func
                    print funcAddress
                    pass

            elif opcode == OP_STOP: 
                break

            print '-----', instrlist[self.PC]
            print 'stack = ', self.stack
            print 'local = ', self.local
            
            self.PC += 1


def builtin_print(stack):
    # number of passed arguments and kws
    nkws = stack.pop()
    nargs = stack.pop()
    arglist = []
    for i in range(nargs):
        arglist.append(stack.pop())
    for item in arglist[-1::-1]:
        sys.stdout.write(str(item) + ' ')
    sys.stdout.write('\n')





class RuntimeError(Exception):
    pass

