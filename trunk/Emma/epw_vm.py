import sys
from epw_bytecode import *

''' The Virtual Machine.

'''


class VM(object):

    def __init__(self):
        # The memory segments
        # Each value in the memory segments is an address in the heap
        # e.g. if we have "x=88" and x is the first local variable,
        # so we have self.local[0] = 1, where 1 is the address in the heap
        # and self.heap[1] = 88, i.e. self.heap[self.local[0]] = 88
        self.LCL = 0
        self.ARG = 0
        self.local = [] 
        self.argument = []
        self.temp = []
        self.pointer = []
        self.this = []
        self.that = []
        # the heap
        self.heap = []
        # the working stack
        self.stack = []
        # frame stack
        self.frameStack = []
        # program counter
        self.PC = 0

    def get_segment_index(self, segment, index):
        if segment == M_ARG:
            return self.argument[index]
        elif segment == M_LOCAL:
            return self.local[index]
        elif segment == M_TEMP:
            return self.temp[index]
        elif segment == M_POINTER:
            return self.pointer[index]
        elif segment == M_THIS:
            return self.this[index]
        elif segment == M_THAT:
            return self.that[index]


    def safe_set_segment_index(self, segment, index, heap_address):
        if index < len(segment) and index >= 0:
            segment[index] = heap_address
        elif index == len(segment):
            segment.append(heap_address)
        else:
            raise RuntimeError('Out of segment boundary')


    def set_segment_index(self, segment, index, heap_address):
        if segment == M_ARG:
            self.safe_set_segment_index(self.argument, index, heap_address)
        elif segment == M_LOCAL:
            self.safe_set_segment_index(self.local, index, heap_address)
        elif segment == M_TEMP:
            self.safe_set_segment_index(self.temp, index, heap_address)
        elif segment == M_POINTER:
            self.safe_set_segment_index(self.pointer, index, heap_address)
        elif segment == M_THIS:
            self.safe_set_segment_index(self.this, index, heap_address)
        elif segment == M_THAT:
            self.safe_set_segment_index(self.that, index, heap_address)


    def run(self, instrlist):

        while self.PC < len(instrlist):
            instr = instrlist[self.PC]

            opcode = instr.opcode

            if opcode == OP_PUSH:
                segment, index = instr.args
                self.stack.append(self.get_segment_index(segment, index))

            elif opcode == OP_POP:
                segment, index = instr.args
                heap_address = self.stack.pop()
                self.set_segment_index(segment, index, heap_address)

            elif opcode == OP_JUMP:
                self.PC = args[0]

            elif opcode == OP_FJUMP:
                heap_address = self.stack.pop()
                if not self.heap[heap_address]:
                    self.PC = args[0]
            






class RuntimeError(Exception):
    pass

