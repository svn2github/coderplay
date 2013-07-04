import sys, os
import re

# The memory segments
M_CONSTANT      = 'constant'
M_STATIC        = 'static'
M_ARG           = 'argument'
M_LOCAL         = 'local'
M_THIS          = 'this'
M_THAT          = 'that'
M_POINTER       = 'pointer'
M_TEMP          = 'temp'

# The VM code keywords
VM_FUNCTION     = 'function'
VM_CALL         = 'call'
VM_RETURN       = 'return'
VM_LABEL        = 'label'
VM_GOTO         = 'goto'
VM_IFGOTO       = 'if-goto'
VM_PUSH         = 'push'
VM_POP          = 'pop'
VM_ADD          = 'add'
VM_SUB          = 'sub'
VM_EQ           = 'eq'
VM_GT           = 'gt'
VM_LT           = 'lt'
VM_AND          = 'and'
VM_OR           = 'or'
VM_NEG          = 'neg'
VM_NOT          = 'not'

VM_BIN_OP       = [VM_ADD, VM_SUB, VM_EQ, VM_GT, VM_LT, VM_AND, VM_OR]
VM_UNARY_OP     = [VM_NEG, VM_NOT]

JACK_OP         = {}
JACK_OP[VM_ADD] = '+'
JACK_OP[VM_SUB] = '-'
JACK_OP[VM_EQ]  = '='
JACK_OP[VM_GT]  = '>'
JACK_OP[VM_LT]  = '<'
JACK_OP[VM_AND] = '&'
JACK_OP[VM_OR]  = '|'
JACK_OP[VM_NEG] = '-'
JACK_OP[VM_NOT] = '~'

class StackEmulator(object):

    def __init__(self):
        self.stack = []
        self.that = {}
        self.pointer = {}
        self.pointer['0'] = 'this'
        self.temp = {}

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def run_cmdlist(self, cmdlist, exitPattern=None):
        '''
        Run through the command list till any of the exit patterns is matched.
        Build up program structs along the way.
        '''
        vmNodeList = []
        # vmNode is only built for Let, Return, Call statements.
        # This ensures that no code will be generated for intermediate
        # expressions.
        vmNode = None 
        pc = 0
        while pc < len(cmdlist):
            cmd = cmdlist[pc]

            # check for exit conditions 
            if exitPattern is not None:
                if cmd.startswith(exitPattern):
                    return pc

            # now we can emulate this command
            # Push an item into the stack
            if cmd.startswith(VM_PUSH): # stack + 1
                _, segment, index = cmd.split()
                if segment == M_CONSTANT:
                    self.push(index)
                elif segment == M_THAT:
                    # THAT segment is to use pointer 1's content as address
                    # push that 0 usually is preceded by a pop pointer 1
                    if isinstance(self.pointer['1'], VmBinOpNode):
                        if self.pointer['1'].op == VM_ADD:
                            array = self.pointer['1'].rhs
                            oldIdx = self.pointer['1'].lhs
                            if index != '0':
                                oldIdx = VmBinOpNode(VM_ADD, oldIdx, index)
                            self.push(VmArrayElementNode(array, oldIdx))
                        else:
                            sys.stderr.write('Error on pushing THAT memory segment\n')
                            sys.exit(1)
                    else:
                        array = self.pointer['1']
                        self.push(VmArrayElementNode(array, index))

                elif segment == M_TEMP:
                    self.push(self.temp[index])

                elif segment == M_POINTER:
                    self.push(self.pointer[index])

                else: # static, arg, this, local
                    self.push(segment + '_' + index)

            
            elif cmd.startswith(VM_IFGOTO): # stack - 1
                item = self.pop()
                if cmd.startswith(VM_IFGOTO + ' WHILE_END'):
                    if not isinstance(item, VmUnaryOpNode) or item.op != VM_NOT:
                        sys.stderr.write('Error on parsing WHILE predicate\n')
                        sys.exit(1)
                    else:
                        item = item.operand
                    print 'while (' + str(item) + ') {' # we need to take off the not of this predicate
                    pc_while = self.run_cmdlist(cmdlist[pc+1:], exitPattern=VM_LABEL+' WHILE_END')
                    pc += pc_while + 1
                    print '}'

                elif cmd.startswith(VM_IFGOTO + ' IF_TRUE'):
                    print 'if (' + str(item) + ') {'
                    pc_if = self.run_cmdlist(cmdlist[pc+1:], exitPattern=VM_LABEL+' IF_FALSE')
                    pc += pc_if + 1
                    print '}'

            elif cmd.startswith(VM_GOTO+' IF_END'):
                # we must have an else clause and we must be already in the IF run
                exitPattern = VM_LABEL+' IF_END'
                print '}'
                print 'else {'

            # Pop an item from the stack
            elif cmd.startswith(VM_POP): # stack - 1
                _, segment, index = cmd.split()
                item = self.pop()
                if segment == M_CONSTANT:
                    sys.stderr.write('Cannot pop to CONSTANT memory segment\n')
                    sys.exit(1)
                elif segment == M_THAT:
                    if isinstance(self.pointer['1'], VmBinOpNode):
                        if self.pointer['1'].op == VM_ADD:
                            array = self.pointer['1'].rhs
                            oldIdx = self.pointer['1'].lhs
                            if index != '0':
                                oldIdx = VmBinOpNode(VM_ADD, oldIdx, index)
                            vmNode = VmLetNode(VmArrayElementNode(array, oldIdx), item)
                        else:
                            sys.stderr.write('Error on pushing THAT memory segment\n')
                            sys.exit(1)
                    else:
                        array = self.pointer['1']
                        vmNode = VmLetNode(VmArrayElementNode(array, index), item)

                elif segment == M_TEMP:
                    self.temp[index] = item

                elif segment == M_POINTER:
                    self.pointer[index] = item

                else: # static, arg, this, local
                    vmNode = VmLetNode(segment + '_' + index, item)


            elif cmd.startswith(VM_CALL): # stack - n + 1
                _, funcName, nargs = cmd.split()
                arglist = []
                for ii in range(int(nargs)):
                    arglist.insert(0, self.pop())
                vmNode = VmCallNode(funcName, arglist)
                self.push(vmNode)


            elif cmd.startswith(VM_RETURN): # stack - 1
                item = self.pop()
                vmNode = VmReturnNode(item)

            elif cmd in VM_BIN_OP: # stack - 1
                rhs = self.pop()
                lhs = self.pop()
                self.push(VmBinOpNode(cmd, lhs, rhs))

            elif cmd in VM_UNARY_OP: # stack no change
                operand = self.pop()
                self.push(VmUnaryOpNode(cmd, operand))

            else: # other label, goto, do nothing
                pass

            # output Jack code if the stack is empty and node is certain type
            if len(self.stack) == 0:

                if isinstance(vmNode, VmLetNode) or isinstance(vmNode, VmReturnNode):
                    vmNodeList.append(vmNode)
                    print vmNode
                    vmNode = None

                elif isinstance(vmNode, VmCallNode) and cmd.startswith(VM_POP+' '+M_TEMP):
                    # A Do statement should always be ended by a 'pop temp 0'
                    # Otherwise it is not a do statement
                    vmNode = VmDoNode(vmNode)
                    vmNodeList.append(vmNode)
                    print vmNode
                    vmNode = None

            # increase the program counter
            pc += 1

        # return the ending program counter
        return pc


class VmNode(object):
    pass

class VmBinOpNode(VmNode):

    def __init__(self, op=None, lhs=None, rhs=None):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        ret = str(self.lhs) + ' ' + JACK_OP[self.op] + ' '
        if isinstance(self.rhs, VmBinOpNode) or isinstance(self.rhs, VmUnaryOpNode):
            ret += '(' + str(self.rhs) + ')'
        else:
            ret += str(self.rhs)
        return ret


class VmUnaryOpNode(VmNode):

    def __init__(self, op=None, operand=None):
        self.op = op
        self.operand = operand

    def __repr__(self):
        ret = JACK_OP[self.op]
        if isinstance(self.operand, VmBinOpNode) or isinstance(self.operand, VmUnaryOpNode):
            ret += '(' + str(self.operand) + ')'
        else:
            ret += str(self.operand)
        return ret


class VmArrayElementNode(VmNode):

    def __init__(self, array=None, index=None):
        self.array = array
        self.index = index

    def __repr__(self):
        ret = str(self.array) + '[' + str(self.index) + ']'
        return ret


class VmIfNode(VmNode):

    def __init__(self, predicate=None, ifBody=None, elseBody=None):
        self.predicate = predicate
        self.ifBody = ifBody
        self.elseBody = elseBody

    def __repr__(self):
        ret = 'if (' + str(self.predicate) + ') {'
        return ret

class VmWhileNode(VmNode):

    def __init__(self, predicate=None, body=None):
        self.predicate = predicate
        self.body = None


class VmLetNode(VmNode):

    def __init__(self, lhs=None, rhs=None):
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        ret = 'let ' + str(self.lhs) + ' = ' + str(self.rhs)
        return ret

class VmDoNode(VmNode):

    def __init__(self, call=None):
        self.call = call

    def __repr__(self):
        ret = 'do ' + str(self.call)
        return ret

class VmCallNode(VmNode):

    def __init__(self, funcName=None, arglist=None):
        self.funcName = funcName
        self.arglist = arglist

    def __repr__(self):
        funcName = self.funcName
        argstrlist = []
        for arg in self.arglist:
            if arg == 'this': # honor method call by not showing the hidden arg
                funcName = funcName.split('.')[1]
                continue
            argstrlist.append(str(arg))
        ret = str(funcName) + '('
        ret += ', '.join(argstrlist) + ')'
        return ret

class VmReturnNode(VmNode):

    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        ret = 'return '
        if self.value is not None:
            ret += str(self.value)
        return ret


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



class Decompiler(object):

    def __init__(self, fileStub):
        f = open(fileStub + '.vm')
        self.contents = f.readlines()
        f.close()
        self.className = fileStub
        self.vmemu = StackEmulator()
        self.jackcode = JackCode()


    def addCode(self, *args):
        self.jackcode.addLine(*args)


    def decompileStatic(self):
        '''
        Scan through the file contents and find out all static variables. 
        They must be defined before any of the subroutines.
        '''
        static_variables = []
        regex = re.compile(r'.* (static [0-9]+)')
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
        print '--------------------------------------------------'
        print 'Class ', self.className
        print '--------------------------------------------------'
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


        print '==========='
        print funcName
        print '==========='
        self.vmemu.run_cmdlist(contents)
        print
        
        
        self.addCode('}')



    def matchLines(self, contents, patternList):
        for line, pattern in zip(contents, patternList):
            if not re.compile(pattern).match(line):
                return False
        return True


    def close(self):
        pass



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


