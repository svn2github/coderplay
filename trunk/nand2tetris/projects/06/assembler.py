import sys

compDict = {}
compDict['0']   = '0101010'
compDict['1']   = '0111111'
compDict['-1']  = '0111010'
compDict['D']   = '0001100'
compDict['A']   = '0110000'
compDict['!D']  = '0001101'
compDict['!A']  = '0110001'
compDict['-D']  = '0001111'
compDict['-A']  = '0110011'
compDict['D+1'] = '0011111'
compDict['1+D'] = '0011111'
compDict['A+1'] = '0110111'
compDict['1+A'] = '0110111'
compDict['D-1'] = '0001110'
compDict['A-1'] = '0110010'
compDict['D+A'] = '0000010'
compDict['A+D'] = '0000010'
compDict['D-A'] = '0010011'
compDict['A-D'] = '0000111'
compDict['D&A'] = '0000000'
compDict['A&D'] = '0000000'
compDict['D|A'] = '0010101'
compDict['A|D'] = '0010101'

compDict['M']   = '1110000'
compDict['!M']  = '1110001'
compDict['-M']  = '1110011'
compDict['M+1'] = '1110111'
compDict['1+M'] = '1110111'
compDict['M-1'] = '1110010'
compDict['D+M'] = '1000010'
compDict['M+D'] = '1000010'
compDict['D-M'] = '1010011'
compDict['M-D'] = '1000111'
compDict['D&M'] = '1000000'
compDict['M&D'] = '1000000'
compDict['D|M'] = '1010101'
compDict['M|D'] = '1010101'

destDict = {}
destDict['null']    = '000'
destDict['M']       = '001'
destDict['D']       = '010'
destDict['MD']      = '011'
destDict['A']       = '100'
destDict['AM']      = '101'
destDict['AD']      = '110'
destDict['AMD']     = '111'

jumpDict = {}
jumpDict['null']    = '000'
jumpDict['JGT']     = '001'
jumpDict['JEQ']     = '010'
jumpDict['JGE']     = '011'
jumpDict['JLT']     = '100'
jumpDict['JNE']     = '101'
jumpDict['JLE']     = '110'
jumpDict['JMP']     = '111'

class Code(object):

    def dest(self, mnemonic):
        return destDict[mnemonic]

    def comp(self, mnemonic):
        return compDict[mnemonic]

    def jump(self, mnemonic):
        return jumpDict[mnemonic]


A_COMMAND = 0
C_COMMAND = 1
L_COMMAND = 2

class Parser(object):

    def __init__(self, filename):
        f = open(filename)
        self.lines = f.readlines()
        f.close()
        self.tidy() # remove all comments and empty lines
        self.cur_command = None
        self.pos = -1

    def tidy(self):
        for ii in range(len(self.lines)-1,-1,-1):
            line = self.lines[ii].strip()
            if line == '':
                del self.lines[ii]
            elif line[0:2] == '//':
                del self.lines[ii]


    def hasMoreCommands(self):
        return True if self.pos < len(self.lines)-1 else False

    def advance(self):
        self.pos += 1
        line = self.lines[self.pos]
        idx = line.find('//') # remove the comments
        if idx >= 0:
            line = line[0:idx]
        self.cur_command = line.strip() # remove any whitespaces

    def commandType(self):
        if self.cur_command[0] == '@':
            return A_COMMAND
        elif self.cur_command[0] == '(':
            return L_COMMAND
        else:
            return C_COMMAND

    def symbol(self):
        if self.cur_command[0] == '@':
            return self.cur_command[1:]
        else:
            return self.cur_command[1:-1]

    def dest(self):
        idx_assign = self.cur_command.find('=')
        if idx_assign < 0:
            return 'null'
        else:
            return self.cur_command[0:idx_assign]
        
    def comp(self):
        idx_assign = self.cur_command.find('=')
        idx_semicolon = self.cur_command.find(';')

        start = 0 if idx_assign < 0 else idx_assign+1
        end = None if idx_semicolon < 0 else idx_semicolon
        return self.cur_command[start:end]

    def jump(self):
        idx_semicolon = self.cur_command.find(';')
        if idx_semicolon < 0:
            return 'null'
        else:
            return self.cur_command[idx_semicolon+1:]

    def reset(self):
        self.cur_command = None
        self.pos = -1


class SymbolTable(object):
    def __init__(self):
        self.table = {}
        for i in range(16):
            self.table['R'+str(i)] = i
        self.table['SP'] = 0
        self.table['LCL'] = 1
        self.table['ARG'] = 2
        self.table['THIS'] = 3
        self.table['THAT'] = 4
        self.table['SCREEN'] = 16384
        self.table['KBD'] = 24576

    def addEntry(self, symbol, address):
        self.table[symbol] = address

    def contains(self, symbol):
        return self.table.has_key(symbol)

    def getAddress(self, symbol):
        return self.table[symbol]


def usage(prog):
    sys.stderr.write('usage: %s filename\n' % prog)
    sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage(sys.argv[0])

    infile = sys.argv[1]
    outfile = infile[0:infile.rindex('.')] + '.hack'
    f = open(outfile, 'w')

    # First pass to build the symbol table with the Labels
    parser = Parser(infile)
    symtbl = SymbolTable()
    lineCount = 0
    while parser.hasMoreCommands():
        parser.advance()
        ctype = parser.commandType()

        if ctype == L_COMMAND:
            symbol = parser.symbol()
            if not symtbl.contains(symbol):
                symtbl.addEntry(symbol, lineCount)
                continue # do not increase counter if its a label line
            else:
                sys.stderr.write('Duplicate Label definition: '+symbol+'\n')
                sys.exit(1)

        # line counter 
        lineCount += 1


    # Second pass to generate the code
    parser.reset()
    code = Code()   
    address = 16
    while parser.hasMoreCommands():
        parser.advance()
        ctype = parser.commandType()

        if ctype == C_COMMAND:
            dest = code.dest(parser.dest())
            comp = code.comp(parser.comp())
            jump = code.jump(parser.jump())
            f.write('111' + comp + dest + jump + '\n') 
            print '111' + comp + dest + jump

        elif ctype == A_COMMAND:
            symbol = parser.symbol()
            if symtbl.contains(symbol): # a label
                dexVal = symtbl.getAddress(symbol)
            elif symbol[0] not in ['0','1','2','3','4','5','6','7','8','9']: # a variable
                symtbl.addEntry(symbol, address)
                dexVal = address
                address += 1
            else: # a pure number
                dexVal = int(symbol)

            # convert to binary
            binVal = bin(dexVal)[2:]
            binVal = '0' * (15 - len(binVal)) + binVal
            f.write('0' + binVal + '\n')
            print '0' + binVal

        else: # L_COMMAND doesn't generate code
            pass

    f.close()

