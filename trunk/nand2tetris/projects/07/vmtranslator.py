import sys, os

C_ARITHMETIC        = 0
C_PUSH              = 1
C_POP               = 2
C_LABEL             = 3
C_GOTO              = 4
C_IF                = 5
C_FUNCTION          = 6
C_RETURN            = 7
C_CALL              = 8


class CodeWriter(object):

    def __init__(self, outfile):
        self.outs = open(outfile, 'w')
        self.fname = None
        self.bool_counter = None

    def setFileName(self, filename):
        self.fname = filename # prefix for variables
        self.bool_counter = 0

    def getAddress(self, segment, index):
        if segment == 'local':
            address = 'LCL'
        elif segment == 'argument':
            address = 'ARG'
        elif segment == 'this':
            address = 'THIS'
        elif segment == 'that':
            address = 'THAT'
        elif segment == 'pointer':
            address = 'THIS' if index == 0 else 'THAT'
        return address

    def writeArithmetic(self, command):
        if command in ['add', 'sub', 'eq', 'gt', 'lt', 'and', 'or']:
            # binary op
            codelist = [
                '@SP',  # first operand from stack
                'M=M-1', 
                'A=M', 
                'D=M', 
                '@SP',  # second operand from stack
                'M=M-1', 
                'A=M', 
                'A=M']
        else:
            # unary
            codelist = [
                '@SP', # operand from stack
                'M=M-1', 
                'A=M', 
                'D=M']

        # operations directly supported by CPU instructions
        if command == 'add':
            codelist.extend(['D=A+D'])
        elif command == 'sub':
            codelist.extend(['D=A-D'])
        elif command == 'neg':
            codelist.extend(['D=-D'])
        elif command == 'and':
            codelist.extend(['D=D&A'])
        elif command == 'or':
            codelist.extend(['D=D|A'])
        elif command == 'not':
            codelist.extend(['D=!D'])

        # operations not directly supported by CPU instructions
        elif command in ['eq', 'gt', 'lt']:
            label_1 = self.fname + '.' + str(self.bool_counter) + '.0.' + command
            label_2 = self.fname + '.' + str(self.bool_counter) + '.1.' + command
            self.bool_counter += 1
            codelist += [
                'D=A-D', 
                '@' + label_1]
            if command == 'eq':
                codelist += ['D;JEQ'] 
            elif command == 'gt':
                codelist += ['D;JGT']
            elif command == 'lt':
                codelist += ['D;JLT']

            codelist += [
                'D=0', 
                '@' + label_2, 
                '0;JMP', 
                '(' + label_1 + ')', 
                'D=-1', 
                '(' + label_2 + ')']

        # push back to the stack
        codelist += [
            '@SP',
            'A=M',
            'M=D',
            '@SP',
            'M=M+1']

        # write the code
        self.outs.write('// ' + command + '\n')
        for s in codelist: 
            self.outs.write(s+'\n')
            print s

    def writePushPop(self, command, segment, index):
        if command == 'push':
            # get value from the segment index and save to D regsiter for push
            if segment == 'constant':
                codelist = [
                    '@' + str(index), 
                    'D=A']
            elif segment  == 'temp':
                codelist = [
                    '@' + str(5+index), 
                    'D=M']
            elif segment  == 'static':
                codelist = [
                    '@' + str(16+index),
                    'D=M']
            elif segment == 'pointer':
                codelist = [
                    '@' + self.getAddress(segment, index), 
                    'D=M']
            else:
                codelist = ['@' + self.getAddress(segment, index)]
                if index == 0:
                    codelist += ['A=M']
                elif index == 1:
                    codelist += ['A=M+1']
                else:
                    codelist += [
                        'D=M', 
                        '@' + str(index), 
                        'A=D+A']
                codelist += ['D=M']

            # Push to the stack
            codelist += [
                '@SP', 
                'A=M', 
                'M=D', 
                '@SP', # stack count increase by 1
                'M=M+1']

        else: # pop
            if segment  == 'temp':
                codelist = [
                    '@SP',
                    'M=M-1', # stack count decrease by 1
                    'A=M',
                    'D=M',
                    '@' + str(5+index),
                    'M=D']
            elif segment  == 'static':
                codelist = [
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    '@' + str(16+index),
                    'M=D']
            elif segment == 'pointer':
                codelist = [
                    '@SP',
                    'M=M-1', # stack count decrease by 1
                    'A=M', 
                    'D=M',
                    '@' + self.getAddress(segment, index),
                    'M=D']
            else:
                # store the value to segment index
                if index == 0:
                    codelist = [
                        '@SP',  # get stack data
                        'M=M-1',  # stack count decrease by 1
                        'A=M', 
                        'D=M',
                        '@' + self.getAddress(segment, index),
                        'A=M',
                        'M=D']
                elif index == 1:
                    codelist = [
                        '@SP',  # get stack data
                        'M=M-1',  # stack count decrease by 1
                        'A=M', 
                        'D=M',
                        '@' + self.getAddress(segment, index),
                        'A=M+1',
                        'M=D']
                else:
                    codelist = [
                        '@' + self.getAddress(segment, index), # pointer arithmatic
                        'D=M',  
                        '@' + str(index),
                        'D=D+A',
                        '@R13',
                        'M=D',
                        '@SP', # get stack data
                        'M=M-1', # stack count decrease by 1
                        'A=M',
                        'D=M',
                        '@R13',
                        'A=M',
                        'M=D']

        # Write the code
        self.outs.write('// ' + command + ' ' + segment + ' ' + str(index) + '\n')
        for s in codelist: 
            self.outs.write(s+'\n')
            print s

    def close(self):
        self.outs.write('(end.of.asm)\n')
        self.outs.write('@end.of.asm\n')
        self.outs.write('0;JMP\n')
        self.outs.close()


class Parser(object):
    
    def __init__(self, infile):
        f = open(infile)
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
        if self.cur_command in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
            return C_ARITHMETIC
        elif self.cur_command[0:3] == 'pop':
            return C_POP
        elif self.cur_command[0:4] == 'push':
            return C_PUSH

    def arg1(self):
        c_type = self.commandType()
        if c_type == C_ARITHMETIC:
            return self.cur_command
        else:
            fields = self.cur_command.split()
            return fields[1]

    def arg2(self):
        fields = self.cur_command.split()
        return int(fields[2])


def usage(prog):
    sys.stderr.write('usage: %s filename\n' % prog)
    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage(sys.argv[0])

    arg = sys.argv[1]

    if arg.endswith('.vm') >= 0:
        filestub = arg[0:arg.rindex('.')]
        filelist = [arg]
    else:
        # search files in the directory
        filestub = arg
        filelist = []
        os.chdir(arg)
        for file in os.listdir("."):
            if file.endswith(".vm"):
                filelist.append(file)

    outfile = filestub + '.asm'

    writer = CodeWriter(outfile)
    for file in filelist:
        parser = Parser(file)
        writer.setFileName(file[0:-3])

        while parser.hasMoreCommands():
            parser.advance()
            c_type = parser.commandType()
            
            if c_type == C_ARITHMETIC:
                writer.writeArithmetic(parser.cur_command)
            elif c_type == C_PUSH:
                arg1 = parser.arg1()
                arg2 = parser.arg2()
                writer.writePushPop('push', arg1, arg2)
            elif c_type == C_POP:
                arg1 = parser.arg1()
                arg2 = parser.arg2()
                writer.writePushPop('pop', arg1, arg2)

    writer.close()

