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

JACK_VAR        = {}
JACK_VAR[M_STATIC]      = '_st'
JACK_VAR[M_ARG]         = 'arg'
JACK_VAR[M_LOCAL]       = 'lcl'
JACK_VAR[M_THIS]        = 'fld'

class StackEmulator(object):

    def __init__(self, className, jackcode):
        self.className = className
        self.jackcode = jackcode
        self.stack = []
        self.that = {}
        self.pointer = {}
        self.pointer['0'] = 'this'
        self.temp = {}
        self.funcType = None

    def addCode(self, *args):
        self.jackcode.addLine(*args)

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def run_cmdlist(self, cmdlist, exitPattern=None):
        '''
        Run through the command list till the end or any of the exit patterns 
        is matched.
        Build up program structs along the way and output them if stack is
        empty and the program struct is certain type.
        This function is recursive and called by itself to parse IF and WHILE
        structures.
        '''
        # vmNode is only built for Let, Return, Call statements.
        # This ensures that no code will be generated for intermediate expressions.
        vmNode = None 
        pc = 0 # program counter

        # Loop through the command list
        while pc < len(cmdlist):
            cmd = cmdlist[pc]

            # check for exit condition 
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
                    # In that case, the content saved in pointer 1 is needed
                    # to be converted as array element type from a (most likely
                    # binary operation type.
                    if isinstance(self.pointer['1'], VmBinOpNode):
                        if self.pointer['1'].op == VM_ADD:
                            array = self.pointer['1'].rhs
                            oldIdx = self.pointer['1'].lhs
                            if index != '0':
                                oldIdx = VmBinOpNode(VM_ADD, oldIdx, index)
                            self.push(VmArrayElementNode(array, oldIdx))
                        else:
                            # The binary operation has to be ADD, .i.e. BASE + offset
                            sys.stderr.write('Error on pushing THAT memory segment\n')
                            sys.exit(1)
                    else:
                        array = self.pointer['1']
                        self.push(VmArrayElementNode(array, index))

                elif segment == M_TEMP:
                    self.push(self.temp[index])

                elif segment == M_POINTER:
                    self.push(self.pointer[index])

                else: # static, argument, this, local
                    self.push(JACK_VAR[segment] + '_' + index)
            
            elif cmd.startswith(VM_IFGOTO): # stack - 1
                item = self.pop()
                # We need recursive calls here to solve the IF and WHILE blocks
                if cmd.startswith(VM_IFGOTO + ' WHILE_END'):
                    # The VM code use NOT on WHILE_EXP, so we need to reverse it
                    if not isinstance(item, VmUnaryOpNode) or item.op != VM_NOT:
                        sys.stderr.write('Error on parsing WHILE predicate\n')
                        sys.exit(1)
                    else:
                        item = item.operand
                    self.addCode('while (' + str(item) + ') {')
                    # recursive call
                    pc_while = self.run_cmdlist(cmdlist[pc+1:], exitPattern=VM_LABEL+' WHILE_END')
                    pc += pc_while + 1 # skip the code that has been ran by the recursive call
                    self.addCode('}')

                elif cmd.startswith(VM_IFGOTO + ' IF_TRUE'):
                    self.addCode('if (' + str(item) + ') {')
                    # recursive call and assume it is only a IF-BLOCK, NOT IF-ELSE
                    pc_if = self.run_cmdlist(cmdlist[pc+1:], exitPattern=VM_LABEL+' IF_FALSE')
                    pc += pc_if + 1
                    self.addCode('}')

            elif cmd.startswith(VM_GOTO+' IF_END'):
                # This command can only be reached in a IF recursive call, which
                # is assumed to be IF-BLOCK. Now we run into this command, we know
                # that the assumption is wrong and we got a IF-ELSE block.
                exitPattern = VM_LABEL+' IF_END'  # change the exit pattern to IF-ELSE
                self.addCode('}')
                self.addCode('else {')

            # Pop an item from the stack
            elif cmd.startswith(VM_POP): # stack - 1
                _, segment, index = cmd.split()
                item = self.pop()
                if segment == M_CONSTANT:
                    sys.stderr.write('Cannot pop to CONSTANT memory segment\n')
                    sys.exit(1)
                elif segment == M_THAT:
                    # THAT segment involves array element handling. See comments
                    # in previous PUSH code.
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

                else: # static, argument, this, local
                    vmNode = VmLetNode(JACK_VAR[segment] + '_' + index, item)


            elif cmd.startswith(VM_CALL): # stack - n + 1
                _, callName, nargs = cmd.split()
                className, funcName = callName.split('.')
                arglist = []
                for ii in range(int(nargs)):
                    arglist.insert(0, self.pop())
                if len(arglist) > 0:
                    # If it is this class's method call, we do not need
                    # show the hidden arg and the class name.
                    if arglist[0] == 'this' and self.className==className:
                        arglist = arglist[1:] # get rid of the hidden arg
                        callName = funcName
                vmNode = VmCallNode(callName, arglist)
                self.push(vmNode)


            elif cmd.startswith(VM_RETURN): # stack - 1
                item = self.pop()
                if self.funcType == 'void':
                    vmNode = VmReturnNode()
                else:
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
                    self.addCode(str(vmNode), ';')
                    vmNode = None

                elif isinstance(vmNode, VmCallNode) and cmd.startswith(VM_POP+' '+M_TEMP):
                    # A Do statement should always be ended by a 'pop temp 0'
                    # Otherwise it is not a do statement
                    vmNode = VmDoNode(vmNode)
                    self.addCode(str(vmNode), ';')
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

    def __init__(self, callName=None, arglist=None):
        self.callName = callName
        self.arglist = arglist

    def __repr__(self):
        argstrlist = [str(arg) for arg in self.arglist]
        ret = str(self.callName) + '('
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

    def write(self, file):
        outs = open(file, 'w')
        ws = '    '
        nindent = 0
        for line in self.linelist:
            n = self.indentLevel(line)
            if n == -1:
                nindent -= 1
            outs.write(ws*nindent + line + '\n')
            if n == 1:
                nindent += 1
        outs.close()


class Decompiler(object):

    def __init__(self, fileStub):
        f = open(fileStub + '.vm')
        self.contents = f.readlines()
        f.close()
        self.className = fileStub
        self.jackcode = JackCode()
        self.vmemu = StackEmulator(self.className, self.jackcode)


    def addCode(self, *args):
        self.jackcode.addLine(*args)


    def decompileClass(self):
        '''
        Main entry of the decompiler. Each jack file is a single jack class.
        '''
        self.addCode('class', self.className, '{')

        self.decompileStatic()
        self.decompileField()

        # find start and end positions of all functions
        func_pos = self.getFuncPositions()

        # decompile each functions
        for sLine, eLine in func_pos:
            contents = [line.strip() for line in self.contents[sLine:eLine]]
            self.decompileFunction(contents)

        self.addCode('}')


    def decompileStatic(self):
        '''
        Scan through the file contents and find out all static variables. 
        They must be defined before any of the subroutines.
        '''
        static_varlist = []
        regex = re.compile(r'.* (static [0-9]+)')
        for line in self.contents:
            matched = regex.match(line)
            if matched:
                idx = int(matched.groups()[0].split()[1])
                if idx not in static_varlist:
                    static_varlist.append(idx)
        # sort the index, so the variable definitions come in order.
        # it does not have any real effects, only for eye pleasing
        static_varlist.sort()
        for idx in static_varlist:
            self.addCode('static', 'int', JACK_VAR[M_STATIC]+'_'+str(idx), ';')


    def decompileField(self):
        '''
        Scan through the file contents and find out all field variables. 
        They must be defined before any of the subroutines.
        '''
        field_varlist = []
        regex = re.compile(r'.* (this [0-9]+)')
        for line in self.contents:
            matched = regex.match(line)
            if matched:
                idx = int(matched.groups()[0].split()[1])
                if idx not in field_varlist:
                    field_varlist.append(idx)
        field_varlist.sort()
        for idx in field_varlist:
            self.addCode('field', 'int', JACK_VAR[M_THIS]+'_'+str(idx), ';')

    def getFuncPositions(self):
        '''
        Get the start and ending positions of each function in the class.
        Whenever a new function keyword appears, it means that the previous 
        function has ended.
        '''
        sLines = []
        eLines = []
        iLine = 0
        while iLine < len(self.contents):
            if self.contents[iLine].startswith('function '):
                if len(sLines) > 0:
                    eLines.append(iLine)
                sLines.append(iLine)
            iLine += 1
        eLines.append(len(self.contents))
        return zip(sLines, eLines)


    def decompileFunction(self, contents):
        '''
        Decompile a single function by:
            0. Read the first line to find out the function name
            1. Read first few lines to find out the function kind
            2. Read last 2 lines to find out the function type
            3. scan through to build up the argument list
            4. Run stack emulator to build up the function body
        '''

        # get the function name
        funcName = self.decompileFuncName(contents)

        # find out the function type (void or not)
        funcType = self.decompileFuncType(contents)

        # find out the function kind
        kind, iLine = self.decompileFuncKind(contents)
        
        # Build the argument list for the subroutine
        arglist = self.decompileArgument(contents, kind)

        # Now we can finish the function header
        self.addCode(kind, funcType, funcName, '(', arglist, ')', '{')

        # get rid of the lines that belongs to the function header
        contents = contents[iLine:]

        # build up the local variables for the function
        self.decompileFuncVars(contents)

        # Run through the function body in the Vm Emulator
        self.vmemu.funcType = funcType
        self.vmemu.run_cmdlist(contents)
        
        # Ending curly bracket for the class
        self.addCode('}')


    def decompileFuncName(self, contents):
        # get the function name
        line = contents[0]
        return line.split()[1].split('.')[1]

    
    def decompileFuncType(self, contents):
        line = contents[-2]
        if line == 'push constant 0':
            funcType = 'void'
        elif line == 'push pointer 0': # return this
            funcType = self.className
        else:
            funcType = 'int'
        return funcType


    def decompileFuncKind(self, contents):
        '''
        Read the first few lines to find out the function kind.
        Also return the line position where the function body starts.
        '''
        if self.matchLines(contents[1:], 
                ['push constant .*', 'call Memory.alloc .*']):
            kind = 'constructor'
            # run pass 3 lines after the func def line
            # push constant x
            # call Memory.alloc 1
            # pop pointer 0
            iLine = 4

        elif self.matchLines(contents[1:], ['push argument 0', 'pop pointer 0']):
            kind = 'method'
            # run pass 2 lines after the func def line
            # push argument 0
            # pop pointer 0
            iLine = 3

        else:
            kind = 'function'
            iLine = 1

        return kind, iLine


    def decompileArgument(self, contents, kind):
        '''
        Scan through the function contents and build up the function argument list.
        '''
        # Build the argument list for the subroutine
        arglist = []
        regex = re.compile('.* (argument [0-9]+)')
        for line in contents: # find all unique arguments
            matched = regex.match(line)
            if matched:
                idx = int(matched.groups()[0].split()[1])
                if idx not in arglist:
                    arglist.append(idx)
        # sort the argument, so they come in order. In contrast to static and field
        # variables, this sort is mandatory.
        arglist.sort()
        if kind == 'method': # we don't wanna list the hidden argment
            arglist = ['int '+JACK_VAR[M_ARG]+'_' + str(idx) for idx in arglist if idx != 0]
        else:
            arglist = ['int '+JACK_VAR[M_ARG]+'_' + str(idx) for idx in arglist]
        arglist = ', '.join(arglist)
        return arglist


    def decompileFuncVars(self, contents):
        '''
        Scan through the function body to build up the local variable list.
        '''
        local_varlist = []
        regex = re.compile(r'.* (local [0-9]+)')
        for line in contents:
            matched = regex.match(line)
            if matched:
                idx = int(matched.groups()[0].split()[1])
                if idx not in local_varlist:
                    local_varlist.append(idx)
        local_varlist.sort()
        for idx in local_varlist:
            self.addCode('var', 'int', JACK_VAR[M_LOCAL]+'_'+str(idx), ';')


    def matchLines(self, contents, patternList):
        for line, pattern in zip(contents, patternList):
            if not re.compile(pattern).match(line):
                return False
        return True


    def close(self):
        self.jackcode.printit()
        self.jackcode.write(self.className+'.jack')


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


