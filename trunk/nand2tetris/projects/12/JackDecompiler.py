import sys, os
import re

class JackCode(object):
    def __init__(self):
        self.linelist = []

    def addLine(self, *args):
        line = ''
        for arg in args:
            line += str(arg) + ' '
        self.linelist.append(line.strip())

    def indentLevel(self, line):
        if line.endswith('{'):
            return 1
        elif line.startswith('}'):
            return -1
        else:
            return 0

    def printit(self):
        ws = '    '
        nindent = 0
        for line in self.linelist:
            n = self.indentLevel(line)
            if n == -1:
                nindent -= 1
            print ws*nindent + line
            if n == 1:
                nindent += 1

IF_STATEMENT        = 0
IFELSE_STATEMENT    = 1
WHILE_STATEMENT     = 2
LET_STATEMENT       = 3
DO_STATEMENT        = 4
RETURN_STATEMENT    = 5
STATEMENT_TYPES     = {}
STATEMENT_TYPES[IF_STATEMENT]       = 'IF_STATEMENT'
STATEMENT_TYPES[IFELSE_STATEMENT]   = 'IFELSE_STATEMENT'
STATEMENT_TYPES[WHILE_STATEMENT]    = 'WHILE_STATEMENT'
STATEMENT_TYPES[LET_STATEMENT]      = 'LET_STATEMENT'
STATEMENT_TYPES[DO_STATEMENT]       = 'DO_STATEMENT'
STATEMENT_TYPES[RETURN_STATEMENT]   = 'RETURN_STATEMENT'

class Decompiler(object):

    def __init__(self, fileStub):
        f = open(fileStub + '.vm')
        self.contents = f.readlines()
        f.close()
        self.className = fileStub
        self.jackcode = JackCode()


    def addCode(self, *args):
        self.jackcode.addLine(*args)


    def decompileStatic(self):
        '''
        Scan through the file contents and find out all static variables. 
        They must be defined before any of the subroutines.
        '''
        static_variables = []
        regex = re.compile(r'.*( static [0-9]+)')
        for line in self.contents:
            matched = regex.match(line)
            if matched:
                varname = matched.groups()[0].replace(' ', '_')
                if varname not in static_variables:
                    self.addCode('static', 'int', varname, ';')
                    static_variables.append(varname)


    def decompileField(self):
        '''
        Scan through the file contents and find out all field variables. 
        They must be defined before any of the subroutines.
        '''
        field_variables = []
        regex = re.compile(r'.* (this [0-9]+)')
        for line in self.contents:
            matched = regex.match(line)
            if matched:
                varname = matched.groups()[0].replace(' ', '_')
                if varname not in field_variables:
                    self.addCode('field', 'int', varname, ';')
                    field_variables.append(varname)


    def getFuncPositions(self):
        sLines = []
        eLines = []
        iLine = 0
        while iLine < len(self.contents):
            if self.contents[iLine].startswith('function '):
                if len(sLines) > 0:
                    eLines.append(iLine-1)
                sLines.append(iLine)
            iLine += 1
        eLines.append(len(self.contents)-1)
        return zip(sLines, eLines)


    def decompileClass(self):
        self.addCode('class', self.className, '{')

        self.decompileStatic()
        self.decompileField()

        # find start and end positions of all functions
        func_pos = self.getFuncPositions()

        # decompile each functions
        for sLine, eLine in func_pos:
            contents = [line.strip() for line in self.contents[sLine:eLine+1]]
            self.decompileFunction(contents)

        self.addCode('}')


    def decompileFunction(self, contents):

        iLine = 0
        nLines = len(contents)

        # get the function name
        line = contents[0]
        funcName = line.split()[1].split('.')[1]

        # find out the function type (void or not)
        line = contents[nLines-2]
        if line == 'push constant 0':
            type = 'void'
        elif line == 'push pointer 0': # return this
            type = self.className
        else:
            type = 'int'

        # find out the function kind
        if self.matchLines(contents[1:], 
                ['push constant .*', 'call Memory.alloc .*']):
            kind = 'constructor'
            # run pass 3 lines after the func def
            # push constant x
            # call Memory.alloc 1
            # pop pointer 0
            iLine = 4
        elif self.matchLines(contents[1:], 
                ['push argument 0', 'pop pointer 0']):
            kind = 'method'
            # run pass 2 lines after the func def
            # push argument 0
            # pop pointer 0
            iLine = 3
        else:
            kind = 'function'
            iLine = 1
        
        # Build the parameter list for the subroutine
        max_idx = -1
        regex = re.compile('.* (argument [0-9]+)')
        for line in contents:
            matched = regex.match(line)
            if matched:
                idx = int(matched.groups()[0].split()[1])
                if max_idx < idx:
                    max_idx = idx
        if max_idx > -1:
            parmlist = []
            if kind == 'method':
                for ii in range(1, max_idx+1):
                    parmlist.append('int argument_' + str(ii))
            else:
                for ii in range(max_idx+1):
                    parmlist.append('int argument_' + str(ii))
            parmlist = ', '.join(parmlist)
        else:
            parmlist = ''
        self.addCode(kind, type, funcName, '(', parmlist, ')', '{')


        # get rid of the lines that belongs to the function definition
        contents = contents[iLine:]

        # calculate the stack status so we can get code blocks
        stack = self.calcStackStatus(contents)
        
        # get the code blocks
        codeBlocks = self.getCodeBlocks(contents, stack, 0)

        # loop through the blocks
        for sidx, eidx, stmt_type in codeBlocks:
            self.decompileCodeBlock(contents[sidx:eidx], stack[sidx:eidx], stmt_type)


    
        self.addCode('}')



    def decompileIfStatement(self, contents):
        pass

    def decompileIfElseStatement(self, contents):
        pass

    def decompileWhileStatement(self, contents):
        pass

    def decompileDoStatement(self, contents):
        if len(contents) == 2: # simple function call with no argument
            funcName = contents[0].split()[1]
            self.addCode('do', funcName, '(', ')', ';')

        if len(contents) == 3: # simiple call with 1 argument, including the hidden arg
            fields = contents[0].split()
            funcName = contents[1].split()[1]
            if fields[1] == 'constant':
                varname = fields[2]
            elif contents[0].startswith('push pointer 0'):
                varname = ''
            else:
                varname = '_'.join(fields[1:])
            self.addCode('do', funcName, '(', varname, ')', ';')

        elif contents[0].startswith('push pointer 0'): # method call
            self.decompileArgList(contents[1:-2])

        else:
            self.decompileArgList(contents[0:-2])


    def decompileReturnStatement(self, contents):
        if len(contents) == 2: # simple return
            if contents[0] == 'push constant 0': # void
                self.addCode('return', ';')
            elif contents[0] == 'push pointer 0': # return this
                self.addCode('return', 'this', ';')
            elif contents[0].startswith('push constant'):
                self.addCode('return', contents[0].split()[2], ';')
            else:
                fields = contents[0].split()
                self.addCode('return', '_'.join(fields[1:]), ';')
        else: # return some expression
            pass


    def decompileLetStatement(self, contents):
        if len(contents) == 2: # simple let
            fields = contents[0].split()
            if fields[1] == 'constant':
                rhs = fields[2]
            else:
                rhs = '_'.join(fields[1:])
            fields = contents[1].split()
            lhs = '_'.join(fields[1:])
            self.addCode('let', lhs, '=', rhs, ';')
        else:
            pass


    def calcStackStatus(self, contents):
        # Simulate the stack status through the function and find out the
        # code blocks. A code block is a single Jack language unit, i.e.
        # let, do, if, while, return.
        stack = [0]
        for line in contents:
            if line.startswith('push'):
                stack.append(stack[-1] + 1)
            elif line.startswith('pop'):
                stack.append(stack[-1] - 1)
            elif line.startswith('return'):
                stack.append(stack[-1] - 1)
            elif line.startswith('if-goto'):
                stack.append(stack[-1] - 1)
            elif line in ['add', 'sub', 'and', 'or', 'gt', 'lt', 'eq']:
                stack.append(stack[-1] - 1)
            elif line.startswith('call'):
                n = int(line.split()[2])
                stack.append(stack[-1] - n + 1)
            else:
                stack.append(stack[-1])

        # Get rid of the leading 0, which is mannually added by us, not part
        # of the actual code.
        return stack[1:]

    
    def decompileCodeBlock(self, contents, stack, stmt_type):
        print STATEMENT_TYPES[stmt_type]
        for idx in range(len(contents)):
            line = contents[idx]
            n = stack[idx]
            sout = ''
            for ii in range(5):
                sout += '   %2d' % (n-ii)
            print '     %-30s %15s' % (line, sout)
        print

        if stmt_type == DO_STATEMENT:
            #self.decompileDoStatement(contents)
            if stack[0] > 0:
                stack = [n-stack[0] for n in stack]


        else:
            pass


    def getCodeBlocks(self, contents, stack, pos):
        codeBlocks = []

        lastPos = pos
        while pos < len(stack):
            if stack[pos] == 0: # we might have found a code block
                line = contents[pos]

                if line.startswith('if-goto'): # get all code belong to IF
                    pos, stmt_type = self.getIfBlock(contents, pos)
                    codeBlocks.append((lastPos, pos, stmt_type))
                    lastPos = pos

                elif line.startswith('label WHILE_EXP'): # get all code belong to WHILE
                    pos, stmt_type = self.getWhileBlock(contents, pos)
                    codeBlocks.append((lastPos, pos, stmt_type))
                    lastPos = pos

                elif line.startswith('pop pointer 1'): # unfinished assignment, get all code
                    pos += 1

                else: # a code block is found
                    pos += 1
                    if line.startswith('return'):
                        codeBlocks.append((lastPos, pos, RETURN_STATEMENT))
                    elif line.startswith('pop temp 0'):
                        codeBlocks.append((lastPos, pos, DO_STATEMENT))
                    elif line.startswith('pop'):
                        codeBlocks.append((lastPos, pos, LET_STATEMENT))
                    lastPos = pos
            else: # no zero has been found, continue
                pos += 1

        # the build code blocks
        return codeBlocks



    def getIfBlock(self, contents, pos):
        isIfElse = False
        for idx in range(pos, len(contents)):
            line = contents[idx]
            if line.startswith('goto IF_END'):
                isIfElse = True
            elif line.startswith('label IF_FALSE') and not isIfElse:
                stmt_type = IF_STATEMENT
                break
            elif line.startswith('label IF_END'):
                stmt_type = IFELSE_STATEMENT
                break
        return idx+1, stmt_type


    def getWhileBlock(self, contents, pos):
        for idx in range(pos, len(contents)):
            line = contents[idx]
            if line.startswith('label WHILE_END'):
                stmt_type = WHILE_STATEMENT
                break
        return idx+1, stmt_type



    def decompileArgList(self, contents):
        '''
        Find the code blocks belong to each argument
        '''
        #stack = ''.join([str(n) for n in stack])

        #start = 0
        #regex = re.compile(str(start) + str(start+1))
        #stack.

        #return arglist


    def decompileExpression(self, contents):
        pass
                
                



    def matchLines(self, contents, patternList):
        for line, pattern in zip(contents, patternList):
            if not re.compile(pattern).match(line):
                return False
        return True


    def close(self):
        pass
        #self.jackcode.printit()



def usage(prog):
    sys.stderr.write('usage: %s [file.vm]\n' % prog)
    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) > 2:
        usage(sys.argv[0])

    if len(sys.argv) == 2: # single file as input
        arg = sys.argv[1]
        filelist = [arg]
    else:
        # search files in the directory
        filelist = []
        for file in os.listdir("."):
            if file.endswith(".vm"):
                filelist.append(file)

    # process files
    for file in filelist:
        fileStub = file[0:file.rindex('.')]
        decompiler = Decompiler(fileStub)
        decompiler.decompileClass()

        decompiler.close()





