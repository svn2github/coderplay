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

    def writeArithmetic(self, command):
        if command in ['add', 'sub', 'eq', 'gt', 'lt', 'and', 'or']:
            # binary op
            codelist = [
                '@SP',  # first operand
                'M=M-1', 
                'A=M', 
                'D=M', 
                '@SP',  # second operand
                'M=M-1', 
                'A=M', 
                'A=M', 
            ]
        else:
            # unary
            codelist = [
                '@SP', 
                'M=M-1', 
                'A=M', 
                'D=M', 
            ]

        if command == 'add':
            codelist.extend(['D=D+A'])
        elif command == 'sub':
            codelist.extend(['D=D-A'])
        elif command == 'neg':
            codelist.extend(['D=-D'])
        elif command == 'eq':
            label_1 = self.fname + '.' + str(self.bool_counter) + '.0.' + command
            label_2 = self.fname + '.' + str(self.bool_counter) + '.1.' + command
            self.bool_counter += 1
            codelist += [
                'D=A-D', 
                '@' + label_1, 
                'D;JEQ', 
                'D=0', 
                '@' + label_2, 
                '0;JMP', 
                '(' + label_1 + ')', 
                'D=-1', 
                '(' + label_2 + ')', 
            ]

        elif command == 'gt':
            label_1 = self.fname + '.' + str(self.bool_counter) + '.0.' + command
            label_2 = self.fname + '.' + str(self.bool_counter) + '.1.' + command
            self.bool_counter += 1
            codelist += [
                'D=A-D', 
                '@' + label_1, 
                'D;JGT', 
                'D=0', 
                '@' + label_2, 
                '0;JMP', 
                '(' + label_1 + ')', 
                'D=-1', 
                '(' + label_2 + ')', 
            ]

        elif command == 'lt':
            label_1 = self.fname + '.' + str(self.bool_counter) + '.0.' + command
            label_2 = self.fname + '.' + str(self.bool_counter) + '.1.' + command
            self.bool_counter += 1
            codelist += [
                'D=A-D', 
                '@' + label_1, 
                'D;JLT', 
                'D=0', 
                '@' + label_2, 
                '0;JMP', 
                '(' + label_1 + ')', 
                'D=-1', 
                '(' + label_2 + ')', 
            ]

        elif command == 'and':
            codelist.extend(['D=D&A'])
        elif command == 'or':
            codelist.extend(['D=D|A'])
        elif command == 'not':
            codelist.extend(['D=!D'])

        # push back, the result is left in D
        codelist += [
            '@SP',
            'A=M',
            'M=D',
            '@SP',
            'M=M+1',
        ]


        for s in codelist: 
            self.outs.write(s+'\n')
            print s


    def writePushPop(self, command, segment, index):
        if command == 'push':
            if segment == 'constant':
                codelist = [
                    '@' + str(index), 
                    'D=A', 
                ]
            else:
                codelist = [
                    # get the value from the segment index
                    # save it to D regsiter for push
                    '@'+segment, 
                    'A=M+' + str(index), 
                    'D=M', 
                ]
            codelist += [
                # Get the correct address for SP
                '@SP', 
                'A=M', 
                'M=D', 
                '@SP', 
                'M=M+1', 
            ]
        else: # pop
            codelist = [
                # get value from the stack top
                '@SP', 
                'M=M-1', 
                'A=M', 
                'D=M', 
                # store the value to segment index
                '@'+segment, 
                'A=M+' + str(index), 
                'M=D', 
            ]

        for s in codelist: 
            self.outs.write(s+'\n')
            print s

    def close(self):
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

