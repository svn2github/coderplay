import sys

'''
The CPU Emulator take an ASM file and run through it.
This program is written to help debug the vmtranslator.py program, which fails
to translate the jack OS vm files and Square game vm files correctly (cannot
run on the supplied CPU emulator.
'''

class CPU(object):

    def __init__(self):
        self.ROM = [0] * 32768
        self.RAM = [0] * 24577
        self.A = 0
        self.D = 0
        self.PC = 0
        self.symbol_table = {}
        self.alloc_address = 16 # the address to start allocate user defined variables
        # The information of some commands in the ROM
        # refered by their addresses
        self.romInfo = {}


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
            if line.startswith('//'): # comment
                self.romInfo[address] = line
                continue
            if line.startswith('('): # label
                label = line[1:-1]
                if self.symbol_table.has_key(label):
                    sys.stderr.write('Duplicate label: ' + label + '\n')
                    sys.exit(1)
                else:
                    self.symbol_table[label] = address
                    continue
            
            self.ROM[address] = line.strip() # load into the ROM
            address += 1 # count the address


    def run(self):
        '''
        Run the program loaded in the ROM.
        '''
        for cmd in self.ROM:
            self.run_command(cmd)


    def run_command(self, cmd):
        '''
        Execute the command by effecting the CPU and storage's status.
        '''

        # command types
        # @xxx
        # ALU arithmetics AMD=X+Y
        # Jumps

        if cmd[0] == '@':
            # A COMMAND
            address = cmd[1:]
            if address[0].isdigit(): # raw numbers
                address = int(address)
            else:
                if self.symbol_table.has_key(address): # labels
                    address = self.symbol_table[address]
                else: # user defined variables
                    self.symbol_table[address] = self.alloc_address
                    address = self.alloc_address
                    self.alloc_address += 1
            # load the address into A
            self.A = address

        elif cmd.find(';') >= 0:
            # JUMP
            predicate, jmpcmd = cmd.split(';')
            if predicate.find('=') >= 0:
                # we have a arithmetics and jump
                pass
            else:
                pass

        else: # ALU arithmetics
            dest, expression = cmd.split('=')
            if len(expression) == 3: # perform the calculation
                lhs = expression[0]
                op = expression[1]
                rhs = expression[2]
            elif len(expression) == 1:
                res = getRegisterContent(expression)
            else:
                sys.stderr.write('Cannot decode arithmetic command: ' + cmd + '\n')
                sys.exit(1)

            for reg in dest:
                self.setRegisterContent(reg, res)

    def getRegisterContent(self, reg):
        if reg == 'A':
            return self.A
        elif reg == 'D':
            return self.D
        elif reg == 'M':
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
            self.RAM[self.A] = content
        else:
            sys.stderr.write('Unknown register: ' + reg + '\n')


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


