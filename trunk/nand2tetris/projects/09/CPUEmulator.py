import sys
import operator

'''
The CPU Emulator take an ASM file and run through it.
This program is written to help debug the vmtranslator.py program, which fails
to translate the jack OS vm files and Square game vm files correctly (cannot
run on the supplied CPU emulator.
'''

class CmdInfo(object):
    '''
    Information about command at certain addresses
    '''

    def __init__(self):
        self.info = {}

    def addInfo(self, address, info):
        if not self.info.has_key(address):
            self.info[address] = []
        self.info[address].append(info)

    def printInfo(self, address):
        if self.info.has_key(address):
            for s in self.info[address]:
                print s


class CPU(object):

    def __init__(self):
        self.ROM = [0] * 32768
        self.RAM = [0] * 24577
        self.A = 0
        self.D = 0
        self.PC = 0
        self.exitAddress = -1
        self.alloc_address = 16 # the address to start allocate user defined variables
        self.cmdinfo = CmdInfo()
        self.symbol_table = {}
        # built-in symbols
        self.symbol_table['SP'] = 0
        self.symbol_table['LCL'] = 1
        self.symbol_table['ARG'] = 2
        self.symbol_table['THIS'] = 3
        self.symbol_table['THAT'] = 4
        self.symbol_table['R0'] = 0
        self.symbol_table['R1'] = 1
        self.symbol_table['R2'] = 2
        self.symbol_table['R3'] = 3
        self.symbol_table['R4'] = 4
        self.symbol_table['R5'] = 5
        self.symbol_table['R6'] = 6
        self.symbol_table['R7'] = 7
        self.symbol_table['R8'] = 8
        self.symbol_table['R9'] = 9
        self.symbol_table['R10'] = 10
        self.symbol_table['R11'] = 11
        self.symbol_table['R12'] = 12
        self.symbol_table['R13'] = 13
        self.symbol_table['R14'] = 14
        self.symbol_table['R15'] = 15
        self.symbol_table['SCREEN'] = 16384
        self.symbol_table['KBD'] = 24576
        self.ALUfunc = {}
        self.ALUfunc['+'] = operator.add
        self.ALUfunc['-'] = operator.sub
        self.ALUfunc['&'] = operator.and_
        self.ALUfunc['|'] = operator.or_
        self.ALUfunc['-u'] = operator.neg # unary op
        self.ALUfunc['!u'] = operator.not_ # unary op


    def read_asm(self, asmfile):
        '''
        read in an asm file and preprocess it to build the information
        about jump address and debug directives. The file read is prepared
        to be loaded into ROM.
        '''
        f = open(asmfile)
        asmlist = f.readlines()
        f.close()

        # preprocess for jump info etc.
        address = 0
        for line in asmlist:

            line = line.strip()

            if line.startswith('//'): # comment
                self.cmdinfo.addInfo(address, line)
                continue

            if line.startswith('('): # label
                label = line[1:-1]
                if self.symbol_table.has_key(label):
                    sys.stderr.write('Duplicate label: ' + label + '\n')
                    sys.exit(1)
                else:
                    self.symbol_table[label] = address
                    self.cmdinfo.addInfo(address, line)
                    if label == 'Sys.halt':
                        self.exitAddress = address
                    continue
            
            self.ROM[address] = line # load into the ROM
            address += 1 # count the address


    def run(self):
        '''
        Run the program loaded in the ROM.
        Execute the command by effecting the CPU and storage's status.
        '''
        while self.PC != self.exitAddress:
            cmd = self.ROM[self.PC]

            self.cmdinfo.printInfo(self.PC)
            sys.stdout.write(str(self.PC) + ':')

            # proceed according to command types
            if cmd[0] == '@': # A Command

                address = cmd[1:]
                if address[0].isdigit(): # raw numbers
                    address = int(address)

                else: # symbols
                    if self.symbol_table.has_key(address): # labels
                        address = self.symbol_table[address]
                    else: # user defined variables
                        self.symbol_table[address] = self.alloc_address
                        address = self.alloc_address
                        self.alloc_address += 1

                # load the address into A
                self.A = address

                # increase the program counter
                self.PC += 1

            else: # C Command

                dest = None
                jump = None
                if cmd.find('=') >= 0: # we have a calculation
                    dest, rest = cmd.split('=')
                else:
                    rest = cmd

                if cmd.find(';') >= 0: # we have a jump
                    expression, jump = rest.split(';')
                else:
                    expression = rest

                if len(expression) == 3: # perform the calculation
                    res = self.binOp(expression[0], expression[1], expression[2])

                elif len(expression) == 2:
                    res = self.unaryOp(expression[0], expression[1])

                elif len(expression) == 1:
                    res = self.getValue(expression)

                else:
                    sys.stderr.write('Cannot decode arithmetic command: ' + cmd + '\n')
                    sys.exit(1)

                # send the result to destination registers
                if dest: # we ensure the A register is effected the last
                    # otherwise, it will mess up with M register content
                    dest = list(dest)
                    dest.sort(reverse=True)
                    dest = ''.join(dest)
                    for reg in dest:
                        self.setRegisterContent(reg, res)

                # process any jumps
                if jump:
                    isJumped = False
                    if jump == 'JMP':
                        self.PC = self.A
                        isJumped = True
                    elif res < 0 and jump in ['JLT', 'JLE', 'JNE']:
                        self.PC = self.A
                        isJumped = True
                    elif res == 0 and jump in ['JEQ', 'JLE', 'JGE']:
                        self.PC = self.A
                        isJumped = True
                    elif res > 0 and jump in ['JGT', 'JGE', 'JNE']:
                        self.PC = self.A
                        isJumped = True
                    if not isJumped:
                        self.PC += 1
                else:
                    # increase the program counter
                    self.PC += 1

            #if self.A == 154 and cmd == 'D;JEQ':
            #    raise Exception
            print cmd, self.A, self.D, self.RAM[0:16]
            # void = raw_input()


    def getRegisterContent(self, reg):
        if reg == 'A':
            return self.A
        elif reg == 'D':
            return self.D
        elif reg == 'M':
            if self.A < 0:
                sys.stderr.write('RAM address cannot be negative: ' + str(self.A) + '\n')
                sys.exit(1)
            return self.RAM[self.A]
        else:
            sys.stderr.write('Unknown register: ' + reg + '\n')
            sys.exit(1)


    def setRegisterContent(self, reg, content):
        if reg == 'A':
            self.A = content
        elif reg == 'D':
            self.D = content
        elif reg == 'M':
            if self.A < 0:
                sys.stderr.write('RAM address cannot be negative: ' + str(self.A) + '\n')
                sys.exit(1)
            self.RAM[self.A] = content
        else:
            sys.stderr.write('Unknown register: ' + reg + '\n')


    def binOp(self, lhs, op, rhs):
        # get the values for lhs and rhs
        lhs = self.getValue(lhs)
        rhs = self.getValue(rhs)
        return self.ALUfunc[op](lhs, rhs)


    def unaryOp(self, op, operand):
        operand = self.getValue(operand)
        return self.ALUfunc[op+'u'](operand)


    def getValue(self, expression):
        value = int(expression) if expression.isdigit() else self.getRegisterContent(expression)
        return value




def usage(prog):
    sys.stderr.write('usage: %s file.asm\n' % prog)
    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage(sys.argv[0])

    asmfile = sys.argv[1]

    cpuEmu = CPU()
    cpuEmu.read_asm(asmfile)
    cpuEmu.run()


