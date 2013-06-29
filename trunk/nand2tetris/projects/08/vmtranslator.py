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
        self.outfile = outfile
        self.outs = open(outfile, 'w')
        self.fname = None
        self.codelist = []
        self.label_counter = 0
        self.bool_counter = None
        self.functionName = 'null'

    def setFileName(self, filename):
        self.fname = filename # the file to process, prefix for variables
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

    def writeCommonCall(self):
        'Assume the return address is saved in R13 and numArgs is saved in R14'
        self.codelist += [
            '(GLOBAL_COMMON_CALL)',
            '@R13',  # get the return address
            'D=M']
        self.writePushStack() 

        # save LCL
        self.codelist += [
            '@LCL',
            'D=M']
        self.writePushStack() 

        # save ARG
        self.codelist += [
            '@ARG',
            'D=M']
        self.writePushStack() 

        # save THIS
        self.codelist += [
            '@THIS',
            'D=M']
        self.writePushStack() 

        # save THAT
        self.codelist += [
            '@THAT',
            'D=M']
        self.writePushStack() 

        # reposition ARG for callee
        self.codelist += [
            '@SP', 
            'D=M', 
            '@R14',  # get numArgs
            'D=D-M', 
            '@5', 
            'D=D-A', 
            '@ARG', 
            'M=D']

        # reposition LCL for callee
        self.codelist += [
            '@SP',
            'D=M',
            '@LCL',
            'M=D']

        # transfer control to callee
        self.codelist += [
            '@R15', # get the function address
            'A=M',
            '0;JMP']


    def writeComments(self, s):
        self.codelist += ['// ' + s]

    def writePopStack(self, register='D'):
        'Get the data from stack and save in a register, default is D'
        self.codelist += [
            '@SP',
            'M=M-1', # stack count decrease by 1
            'A=M',
            register + '=M']

    def writePushStack(self, register='D'):
        'Push the data from register to stack'
        self.codelist += [
            '@SP',
            'A=M', 
            'M=D', 
            '@SP', 
            'M=M+1'] # stack top address increase by 1

    def writeArithmetic(self, command):

        self.writePopStack() # get 1st operand from stack and save to D register
        # for binary op we get 2nd operand
        if command in ['add', 'sub', 'eq', 'gt', 'lt', 'and', 'or']: # binary op
            self.writePopStack('A') # get 2nd operand from stack and save to A register

        # Arithmetic operations directly supported by CPU instructions
        if command == 'add':
            self.codelist += ['D=A+D']
        elif command == 'sub':
            self.codelist += ['D=A-D']
        elif command == 'neg':
            self.codelist += ['D=-D']
        elif command == 'and':
            self.codelist += ['D=D&A']
        elif command == 'or':
            self.codelist += ['D=D|A']
        elif command == 'not':
            self.codelist += ['D=!D']

        # boolean operations not directly supported by CPU instructions
        # we have to use jumps for boolean tests
        elif command in ['eq', 'gt', 'lt']:
            label_1 = self.fname + '.' + str(self.bool_counter) + '.true.' + command
            label_2 = self.fname + '.' + str(self.bool_counter) + '.end.' + command
            self.bool_counter += 1
            self.codelist += [
                'D=A-D', 
                '@' + label_1]
            if command == 'eq':
                self.codelist += ['D;JEQ'] 
            elif command == 'gt':
                self.codelist += ['D;JGT']
            elif command == 'lt':
                self.codelist += ['D;JLT']

            self.codelist += [
                'D=0', 
                '@' + label_2, 
                '0;JMP', 
                '(' + label_1 + ')', 
                'D=-1', 
                '(' + label_2 + ')']

        # push back to the stack
        self.writePushStack()


    def writePushPop(self, command, segment, index):
        '''
        Push data
            1. Get address of the data to be pushed (pointer calculations
               may be needed for get the correct address of a segment)
            2. Get the data and save it to D
            3. Push the Data from D to the stack (stack management is needed)
        Pop data
              If the index into a segment is less than or equal to 1, the
            pointer calculation is supported by direct CPU instruction.
            So it is simply as
            1. Get the data from stack and store to D register
            2. Get the address of the index of the segment, store in A
            3. Store content of D to M[A]
              If index is 2 or up, the address of the segment index has to
            be calculated first and store in R13. We can then start the above
            three steps.
        '''

        if command == C_PUSH:
            # get value from the segment index and save to D regsiter for push
            if segment == 'constant':
                self.codelist += [
                    '@' + str(index), 
                    'D=A']
            elif segment  == 'temp':
                self.codelist += [
                    '@' + str(5+index), 
                    'D=M']
            elif segment  == 'static':
                self.codelist += [
                    '@' + self.fname + '.' + str(index),
                    'D=M']
            elif segment == 'pointer':
                self.codelist += [
                    '@' + self.getAddress(segment, index), 
                    'D=M']
            else:
                self.codelist += ['@' + self.getAddress(segment, index)]
                # index 0 and 1 have direct CPU support
                # index 2 and up have to do extra work
                if index == 0:
                    self.codelist += ['A=M']
                elif index == 1:
                    self.codelist += ['A=M+1']
                else:
                    self.codelist += [
                        'D=M', 
                        '@' + str(index), 
                        'A=D+A']
                self.codelist += ['D=M']

            # Push to the stack
            self.writePushStack()

        else: # pop
            if segment in ['temp', 'static', 'pointer']:
                self.writePopStack()
                if segment  == 'temp':
                    self.codelist += ['@' + str(5+index)]
                elif segment  == 'static':
                    self.codelist += ['@' + self.fname + '.' + str(index)]
                elif segment == 'pointer':
                    self.codelist += ['@' + self.getAddress(segment,index)]

            else:
                # store the value to segment index
                if index <= 1:
                    self.writePopStack()
                    self.codelist += [
                        '@' + self.getAddress(segment, index),
                        'A=M' + ('+1' if index ==1 else '')]
                else:
                    # first get the correct pointer address by pointer arithmatic
                    # the calculated address is saved in R13
                    self.codelist += [
                        '@' + self.getAddress(segment, index), 
                        'D=M',  
                        '@' + str(index),
                        'D=D+A',
                        '@R13',
                        'M=D']
                    self.writePopStack() # get data from stack and save to D
                    self.codelist += [
                        '@R13',
                        'A=M']

            # We assign the content of segment index to the content of D register
            # This finish the entire pop operation
            self.codelist += ['M=D']


    def writeLabel(self, label):
        if self.functionName:
            label = self.functionName + '$' + label
        self.codelist += ['(' + label + ')']

    def writeGoto(self, label):
        if self.functionName:
            label = self.functionName + '$' + label
        self.codelist += [
            '@' + label, 
            '0;JMP']

    def writeIf(self, label):
        # compare to 0
        self.writePushPop(C_PUSH, 'constant', 0)
        self.writeArithmetic('eq')  
        # if test==0 we have -1 on stack top, so no jump
        # thus jump if a 0 on stack top
        self.writePopStack() # get the stack top to D register
        if self.functionName:
            label = self.functionName + '$' + label
        self.codelist += [
            '@' + label,
            'D;JEQ'] 

    def writeFunction(self, functionName, numLocals):
        self.codelist += ['(' + functionName + ')']
        for ii in range(numLocals):
            self.writePushPop(C_PUSH, 'constant', 0)
            self.writePushPop(C_POP, 'local', ii)
        self.functionName = functionName

    def writeReturn(self):
        self.codelist += [
            '@LCL', 
            'D=M',
            '@R5',
            'M=D',  # save as frame
            '@5',   # start calculting the return address
            'D=A',
            '@R5',
            'A=M-D',
            'D=M',
            '@R6',
            'M=D']  # the return address

        # Put the return value
        self.writePushPop(C_POP, 'argument', 0)

        self.codelist += [
            # restore caller's SP
            '@ARG', 
            'D=M+1', 
            '@SP', 
            'M=D', 

            # restore caller's THAT
            '@R5', 
            'A=M-1', 
            'D=M', 
            '@THAT', 
            'M=D', 

            # restore caller's THIS
            '@R5', 
            'D=M', 
            '@2', 
            'A=D-A', 
            'D=M', 
            '@THIS', 
            'M=D', 

            # restore caller's ARG
            '@R5', 
            'D=M', 
            '@3', 
            'A=D-A', 
            'D=M', 
            '@ARG', 
            'M=D', 

            # restore caller's LCL
            '@R5', 
            'D=M', 
            '@4', 
            'A=D-A', 
            'D=M', 
            '@LCL', 
            'M=D', 

            # go to retAddress
            '@R6', 
            'A=M', 
            '0;JMP']


    def writeCall(self, functionName, numArgs):
        returnLabel = functionName + '$L_Return.' + str(self.label_counter)
        self.label_counter += 1

        # save return address to stack
        self.codelist += [
            '@' + returnLabel,
            'D=A',
            '@R13', # save return address to R13
            'M=D', 
            '@' + str(numArgs), 
            'D=A', 
            '@R14', # save numArgs to R14
            'M=D', 
            '@' + functionName,
            'D=A', 
            '@R15', # save the function address to R15
            'M=D',
            '@GLOBAL_COMMON_CALL',
            '0;JMP']

        # the return address
        self.codelist += ['(' + returnLabel + ')']


    def writeInit(self):
        self.codelist += [
            '@256',
            'D=A',
            '@SP',
            'M=D']
        self.writeCall('Sys.init', 0)

    def writeDebug(self, address=19999):
        self.codelist += [
            '@' + str(address),
            'M=1',
            'M=0']

    def close(self):
        'Write out the file and close it'
        for s in self.codelist:
            self.outs.write(s + '\n')
            print s
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
        elif self.cur_command.startswith('pop'):
            return C_POP
        elif self.cur_command.startswith('push'):
            return C_PUSH
        elif self.cur_command.startswith('label'):
            return C_LABEL
        elif self.cur_command.startswith('goto'):
            return C_GOTO
        elif self.cur_command.startswith('if-goto'):
            return C_IF
        elif self.cur_command.startswith('function'):
            return C_FUNCTION
        elif self.cur_command.startswith('call'):
            return C_CALL
        elif self.cur_command.startswith('return'):
            return C_RETURN

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
    if len(sys.argv) > 2:
        usage(sys.argv[0])

    if len(sys.argv) == 2:
        arg = sys.argv[1]
        filestub = arg[0:arg.rindex('.')]
        filelist = [arg]
    else:
        # search files in the directory
        filestub = os.getcwd().split(os.sep)[-1]
        filelist = []
        for file in os.listdir("."):
            if file.endswith(".vm"):
                filelist.append(file)

    outfile = filestub + '.asm'

    writer = CodeWriter(outfile)
    writer.writeInit()
    writer.writeCommonCall()

    for file in filelist:
        parser = Parser(file)
        writer.setFileName(file[0:-3])

        while parser.hasMoreCommands():
            parser.advance()
            c_type = parser.commandType()

            # Save the original vm code as comments
            writer.writeComments(parser.cur_command)
            
            if c_type == C_ARITHMETIC:
                writer.writeArithmetic(parser.arg1())

            elif c_type in [C_PUSH, C_POP]:
                arg1 = parser.arg1()
                arg2 = parser.arg2()
                writer.writePushPop(c_type, arg1, arg2)

            elif c_type == C_LABEL:
                writer.writeLabel(parser.arg1())

            elif c_type == C_GOTO:
                writer.writeGoto(parser.arg1())

            elif c_type == C_IF:
                writer.writeIf(parser.arg1())

            elif c_type == C_FUNCTION:
                writer.writeFunction(parser.arg1(), parser.arg2())

            elif c_type == C_RETURN:
                writer.writeReturn()

            elif c_type == C_CALL:
                writer.writeCall(parser.arg1(), parser.arg2())

            #writer.writeDebug()

    # clean up the writer
    writer.close()


