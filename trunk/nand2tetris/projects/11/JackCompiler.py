import sys, os
import re


# The kind of variables
K_STATIC  = 'static'
K_FIELD   = 'field'
K_ARG     = 'argument'
K_VAR     = 'var'

class SymbolTable(object):

    def __init__(self):
        self.class_scope = {} # class scope
        self.sub_scope = {} # subroutine scope
        self.nStatic = 0
        self.nField = 0
        self.nArgs = 0
        self.nVars = 0

    def startSubroutine(self, kind):
        self.sub_scope = {}
        self.nVars = 0
        # Note that the method subroutine has a hidden 'this' parameter
        # So the count starts from 1 instead of 0.
        if kind == KW_METHOD:
            self.nArgs = 1
        else:
            self.nArgs = 0

    def define(self, name, type, kind):
        if self.indexOf(name) is not None:
            sys.stderr.write('Duplicate declaration of variable: ' + name + '\n')
            sys.exit(1)

        if kind == K_STATIC:
            idx = self.nStatic
            self.class_scope[name] = [type, kind, idx]
            self.nStatic += 1
        elif kind == K_FIELD:
            idx = self.nField
            self.class_scope[name] = [type, kind, idx]
            self.nField += 1
        elif kind == K_ARG:
            idx = self.nArgs
            self.sub_scope[name] = [type, kind, idx]
            self.nArgs += 1
        else: # kind == K_VAR
            idx = self.nVars
            self.sub_scope[name] = [type, kind, idx]
            self.nVars += 1

    def varCount(self, kind):
        if kind == K_STATIC:
            return self.nStatic
        elif kind == K_FIELD:
            return self.nField
        elif kind == K_ARG:
            return self.nArgs
        else: #kind == K_VAR
            return self.nVars

    def kindOf(self, name):
        if self.class_scope.has_key(name):
            return self.class_scope[name][1]
        elif self.sub_scope.has_key(name):
            return self.sub_scope[name][1]
        else:
            return None

    def typeOf(self, name):
        if self.class_scope.has_key(name):
            return self.class_scope[name][0]
        elif self.sub_scope.has_key(name):
            return self.sub_scope[name][0]
        else:
            return None

    def indexOf(self, name):
        if self.class_scope.has_key(name):
            return self.class_scope[name][2]
        elif self.sub_scope.has_key(name):
            return self.sub_scope[name][2]
        else:
            return None


# The memory segments
M_CONSTANT      = 'constant'
M_STATIC        = 'static'
M_ARG           = 'argument'
M_LOCAL         = 'local'
M_THIS          = 'this'
M_THAT          = 'that'
M_POINTER       = 'pointer'
M_TEMP          = 'temp'

class VMWriter(object):

    def __init__(self, fileStub):
        self.outs = open(fileStub + '.vm', 'w')

    def write(self, *args):
        self.outs.write(str(args[0]))
        for arg in args[1:]:
            self.outs.write(' ' + str(arg))
        self.outs.write('\n')

    def writePush(self, segment, index):
        self.write('push', segment, index)

    def writePop(self, segment, index):
        self.write('pop', segment, index)

    def writeArithmetic(self, command, unary=False):
        if command == SYM_ADD:
            self.write('add')
        elif command == SYM_SUB:
            if unary:
                self.write('neg')
            else:
                self.write('sub')
        elif command == SYM_EQ:
            self.write('eq')
        elif command == SYM_GT:
            self.write('gt')
        elif command == SYM_LT:
            self.write('lt')
        elif command == SYM_AND:
            self.write('and')
        elif command == SYM_OR:
            self.write('or')
        elif command == SYM_NOT:
            self.write('not')
        elif command == SYM_MUL:
            self.writeCall('Math.multiply', 2)
        elif command == SYM_DIV:
            self.writeCall('Math.divide', 2)

    def writeLabel(self, label):
        self.write('label', label)

    def writeGoto(self, label):
        self.write('goto', label)

    def writeIf(self, label):
        self.write('if-goto', label)

    def writeCall(self, name, nArgs):
        self.write('call', name, nArgs)

    def writeFunction(self, name, nLocals):
        self.write('function', name, nLocals)

    def writeReturn(self):
        self.write('return')

    def close(self):
        self.outs.close()


def writeToken(outs, tType, tValue, indent=0):
    if tValue == SYM_LT:
        tValue = '&lt;'
    elif tValue == SYM_GT:
        tValue = '&gt;'
    elif tValue == SYM_AND:
        tValue ='&amp;'

    # Set for the correct tType and tValue
    if tType == T_INT_CONST:
        tValue = int(tValue)
    elif tType == T_STRING_CONST: 
        tValue = tValue[1:-1] # strip double quotes

    # output to file
    outs.write('  '*indent + '<' + tType + '> ' + str(tValue) 
            + ' </' + tType + '>\n')


def writeStruct(outs, struct, indent=0, close=False):
    outs.write('  '*indent + '<' 
            + ('/' if close else '') + struct + '>\n')


class CompilationEngine(object):

    def __init__(self, fileStub, tokenizer, symtab, vmwriter):
        self.className = fileStub
        self.tokenizer = tokenizer # input
        self.symtab = symtab
        self.vmwriter = vmwriter
        self.outs = open(fileStub + '.xml', 'w')
        self.indent = 0
        self.while_label_count = 0
        self.if_label_count = 0

    def getSegementOfKind(self, kind):
        if kind == K_STATIC:
            return M_STATIC
        elif kind == K_FIELD:
            return M_THIS
        elif kind == K_ARG:
            return M_ARG
        else: # kind == K_VAR:
            return M_LOCAL

    def match(self, tType, tValue=None):
        '''
        Match and write a token
        '''
        tType, tValue = self.tokenizer.match(tType, tValue)
        writeToken(self.outs, tType, tValue, self.indent)
        return tType, tValue

    def nextTokenIsType(self, tType):
        return True if self.tokenizer.cur_type == tType else False

    def nextTokenIsValue(self, tValue):
        if type(tValue) == list:
            return True if self.tokenizer.cur_value in tValue else False
        else:
            return True if self.tokenizer.cur_value == tValue else False

    def compileClass(self):
        success = self.tokenizer.advance()  # get the 1st token
        if not success: # if the file is empty
            return

        # Starting match the class struct
        writeStruct(self.outs, 'class', self.indent)
        self.indent += 1

        self.match(T_KEYWORD, KW_CLASS) # match and get next token
        self.match(T_IDENTIFIER, self.className)
        self.match(T_SYMBOL, SYM_L_CURLY)

        # Try to figure out what struct comes next
        while True: # variables for the class
            if self.nextTokenIsType(T_KEYWORD) \
                    and self.nextTokenIsValue([KW_STATIC, KW_FIELD]):
                self.compileClassVarDec()
            else:
                break
           
        while True: # subroutines for the class
            if self.nextTokenIsType(T_KEYWORD) \
                    and self.nextTokenIsValue([KW_CONSTRUCTOR, KW_FUNCTION, KW_METHOD]):
                self.compileSubroutine()
            else:
                break

        # End of the class definition
        self.match(T_SYMBOL, SYM_R_CURLY)

        self.indent -= 1
        writeStruct(self.outs, 'class', self.indent, True)

    def compileClassVarDec(self):
        '''
        Gather the class scope variable information, no vm code here.
        '''

        # start parsing 
        writeStruct(self.outs, 'classVarDec', self.indent)
        self.indent += 1
        _, kind = self.match(T_KEYWORD, [KW_STATIC, KW_FIELD]) # static, field
        # type | className
        if self.nextTokenIsType(T_KEYWORD):
            _, type = self.match(T_KEYWORD, [KW_INT, KW_CHAR, KW_BOOLEAN])
        else:
            _, type = self.match(T_IDENTIFIER)
        _, name = self.match(T_IDENTIFIER) # varName

        # add to the symbol table
        self.symtab.define(name, type, kind)

        # list of vars
        while self.nextTokenIsValue(SYM_COMMA): # (',' varName)* 
            self.match(T_SYMBOL, SYM_COMMA)
            _, name = self.match(T_IDENTIFIER)
            self.symtab.define(name, type, kind) # add to symbol table

        # End of class variable declaration
        self.match(T_SYMBOL, SYM_SEMICOLON) # ';'
        # closing
        self.indent -= 1
        writeStruct(self.outs, 'classVarDec', self.indent, True)


    def compileSubroutine(self):

        writeStruct(self.outs, 'subroutineDec', self.indent)
        self.indent += 1

        # the subroutine kind
        _, kind = self.match(T_KEYWORD, [KW_CONSTRUCTOR, KW_FUNCTION, KW_METHOD])

        # reset the function scope
        self.symtab.startSubroutine(kind) 
        # reset label counts for each every subroutine
        self.while_label_count = 0
        self.if_label_count = 0

        # the subroutine return type
        if self.nextTokenIsType(T_KEYWORD):
            self.match(T_KEYWORD, [KW_VOID, KW_INT, KW_CHAR, KW_BOOLEAN])
        else:
            self.match(T_IDENTIFIER)

        _, name = self.match(T_IDENTIFIER) # subroutineName
        name = self.className + '.' + name # attach the class name to the function name

        # parameter list
        self.match(T_SYMBOL, SYM_L_PAREN)
        self.compileParameterList() 
        self.match(T_SYMBOL, SYM_R_PAREN)

        # subroutine body
        self.compileSubroutineBody(name, kind)

        # closing
        self.indent -= 1
        writeStruct(self.outs, 'subroutineDec', self.indent, True)


    def compileParameterList(self):
        '''
        Parameter list for function definition. Gather subroutine scope variable
        information here. No vm code.
        '''

        writeStruct(self.outs, 'parameterList', self.indent)
        self.indent += 1

        # check if empty parameter list
        if not self.nextTokenIsValue(SYM_R_PAREN):
            # type
            if self.nextTokenIsType(T_KEYWORD):
                _, type = self.match(T_KEYWORD, [KW_INT, KW_CHAR, KW_BOOLEAN])
            else:
                _, type = self.match(T_IDENTIFIER)
            _, name = self.match(T_IDENTIFIER) # varName
            # add to symbol table
            self.symtab.define(name, type, K_ARG)
            # following vars
            while self.nextTokenIsValue(SYM_COMMA):
                self.match(T_SYMBOL, SYM_COMMA) # ',' type varName
                if self.nextTokenIsType(T_KEYWORD):
                    _, type = self.match(T_KEYWORD, [KW_INT, KW_CHAR, KW_BOOLEAN])
                else:
                    _, type = self.match(T_IDENTIFIER)
                _, name = self.match(T_IDENTIFIER)
                self.symtab.define(name, type, K_ARG)

        self.indent -= 1
        writeStruct(self.outs, 'parameterList', self.indent, True)


    def compileSubroutineBody(self, name, kind):
        writeStruct(self.outs, 'subroutineBody', self.indent)
        self.indent += 1
        self.match(T_SYMBOL, SYM_L_CURLY)

        # variable declaration
        while self.nextTokenIsValue(KW_VAR):
            self.compileVarDec()

        # write out the function definition line
        nLocals = self.symtab.varCount(K_VAR)
        self.vmwriter.writeFunction(name, nLocals)
        # code for different subroutine kinds
        if kind == KW_CONSTRUCTOR: # need to call Memory.alloc
            nField = self.symtab.varCount(K_FIELD)
            self.vmwriter.writePush(M_CONSTANT, nField)
            self.vmwriter.writeCall('Memory.alloc', 1)
            self.vmwriter.writePop(M_POINTER, 0) # set this
        elif kind == KW_METHOD: # need to deal with hidden argument 0 (this)
            self.vmwriter.writePush(M_ARG, 0) # the hidden argument 0
            self.vmwriter.writePop(M_POINTER, 0) # set this

        # statments
        self.compileStatements()
        self.match(T_SYMBOL, SYM_R_CURLY)
        self.indent -= 1
        writeStruct(self.outs, 'subroutineBody', self.indent, True)


    def compileVarDec(self):
        '''
        Subroutine scope variable information gathering. No vm code.
        '''
        
        # starting mark for xml output
        writeStruct(self.outs, 'varDec', self.indent)
        self.indent += 1

        # kind
        _, kind = self.match(T_KEYWORD, KW_VAR) # 'var'
        # type
        if self.nextTokenIsType(T_KEYWORD):
            _, type = self.match(T_KEYWORD, [KW_INT, KW_CHAR, KW_BOOLEAN])
        else:
            _, type = self.match(T_IDENTIFIER)
        _, name = self.match(T_IDENTIFIER) # varName
        # add to the symbol table
        self.symtab.define(name, type, kind)

        # list of vars
        while self.nextTokenIsValue(SYM_COMMA):
            self.match(T_SYMBOL, SYM_COMMA) # ',' varName
            _, name = self.match(T_IDENTIFIER)
            self.symtab.define(name, type, kind) # add to symbol table
        self.match(T_SYMBOL, SYM_SEMICOLON)

        # closing mark for xml output
        self.indent -= 1
        writeStruct(self.outs, 'varDec', self.indent, True)


    def compileStatements(self):
        writeStruct(self.outs, 'statements', self.indent)
        self.indent += 1

        while True:
            if self.nextTokenIsValue(KW_LET):
                self.compileLet()
            elif self.nextTokenIsValue(KW_IF):
                self.compileIf()
            elif self.nextTokenIsValue(KW_WHILE):
                self.compileWhile()
            elif self.nextTokenIsValue(KW_DO):
                self.compileDo()
            elif self.nextTokenIsValue(KW_RETURN):
                self.compileReturn()
            else:
                break

        self.indent -= 1
        writeStruct(self.outs, 'statements', self.indent, True)


    def compileDo(self):
        writeStruct(self.outs, 'doStatement', self.indent)
        self.indent += 1

        self.match(T_KEYWORD, KW_DO)
        # subroutine call
        _, name = self.match(T_IDENTIFIER) # class or function name
        self.compileSubroutineCall(name)
        # write the vm code to discard the return value of 0
        self.vmwriter.writePop(M_TEMP, 0)
        self.match(T_SYMBOL, SYM_SEMICOLON)

        self.indent -= 1
        writeStruct(self.outs, 'doStatement', self.indent, True)


    def compileLet(self):
        writeStruct(self.outs, 'letStatement', self.indent)
        self.indent += 1

        self.match(T_KEYWORD, KW_LET)
        # the variable name
        _, name = self.match(T_IDENTIFIER)
        kind = self.symtab.kindOf(name)
        index = self.symtab.indexOf(name)

        # array element
        is_simple_assignment = True
        if self.nextTokenIsValue(SYM_L_BRACKET):
            is_simple_assignment = False
            self.match(T_SYMBOL, SYM_L_BRACKET)
            self.compileExpression()
            self.match(T_SYMBOL, SYM_R_BRACKET)
            # Calculate the element address
            self.vmwriter.writePush(self.getSegementOfKind(kind), index)
            self.vmwriter.writeArithmetic(SYM_ADD)

        # match the right hand side of the assignment
        self.match(T_SYMBOL, SYM_EQ)
        self.compileExpression()

        if is_simple_assignment:
            # write vm code for simple variable assignment
            self.vmwriter.writePop(self.getSegementOfKind(kind), index)
        else: 
            # write vm code for the array element assignment
            self.vmwriter.writePop(M_TEMP, 0)
            self.vmwriter.writePop(M_POINTER, 1)
            self.vmwriter.writePush(M_TEMP, 0)
            self.vmwriter.writePop(M_THAT, 0)

        # the ending ';'
        self.match(T_SYMBOL, SYM_SEMICOLON)

        self.indent -= 1
        writeStruct(self.outs, 'letStatement', self.indent, True)


    def compileWhile(self):
        writeStruct(self.outs, 'whileStatement', self.indent)
        self.indent += 1

        self.match(T_KEYWORD, KW_WHILE)
        # vm code for while label
        label_exp = 'WHILE_EXP' + str(self.while_label_count)
        label_end = 'WHILE_END' + str(self.while_label_count)
        self.while_label_count += 1
        self.vmwriter.writeLabel(label_exp)
        # test expression
        self.match(T_SYMBOL, SYM_L_PAREN)
        self.compileExpression()
        self.match(T_SYMBOL, SYM_R_PAREN)
        # add a not so following if-goto goes to the end of loop
        self.vmwriter.writeArithmetic(SYM_NOT)
        self.vmwriter.writeIf(label_end)
        # loop body
        self.match(T_SYMBOL, SYM_L_CURLY)
        self.compileStatements()
        self.match(T_SYMBOL, SYM_R_CURLY)
        # vm code for loop
        self.vmwriter.writeGoto(label_exp)
        self.vmwriter.writeLabel(label_end)

        self.indent -= 1
        writeStruct(self.outs, 'whileStatement', self.indent, True)


    def compileReturn(self):
        writeStruct(self.outs, 'returnStatement', self.indent)
        self.indent += 1
        self.match(T_KEYWORD, KW_RETURN)
        if not self.nextTokenIsValue(SYM_SEMICOLON):
            self.compileExpression()
            self.vmwriter.writeReturn()

        else: # void function return a hidden 0
            self.vmwriter.writePush(M_CONSTANT, 0)
            self.vmwriter.writeReturn()

        self.match(T_SYMBOL, SYM_SEMICOLON)
        self.indent -= 1
        writeStruct(self.outs, 'returnStatement', self.indent, True)


    def compileIf(self):
        writeStruct(self.outs, 'ifStatement', self.indent)
        self.indent += 1

        self.match(T_KEYWORD, KW_IF)
        self.match(T_SYMBOL, SYM_L_PAREN)
        self.compileExpression()
        self.match(T_SYMBOL, SYM_R_PAREN)
    
        # vm code for label and flow control
        label_true = 'IF_TRUE' + str(self.if_label_count)
        label_false = 'IF_FALSE' + str(self.if_label_count)
        # make the end label in case it is needed
        # this end label should be created here even it may not be needed.
        # if not created here, any nested if statement will mess up 
        # with this label count
        label_end = 'IF_END' + str(self.if_label_count)
        self.if_label_count += 1

        self.vmwriter.writeIf(label_true)
        self.vmwriter.writeGoto(label_false)
        self.vmwriter.writeLabel(label_true)
        
        # if body
        self.match(T_SYMBOL, SYM_L_CURLY)
        self.compileStatements()
        self.match(T_SYMBOL, SYM_R_CURLY)

        # else body
        if self.nextTokenIsValue(KW_ELSE):
            # vm code for flow control
            self.vmwriter.writeGoto(label_end)
            self.vmwriter.writeLabel(label_false)

            self.match(T_KEYWORD, KW_ELSE)
            self.match(T_SYMBOL, SYM_L_CURLY)
            self.compileStatements()
            self.match(T_SYMBOL, SYM_R_CURLY)

            # vm code for end of struct
            self.vmwriter.writeLabel(label_end)

        else: # no else body
            self.vmwriter.writeLabel(label_false)

        self.indent -= 1
        writeStruct(self.outs, 'ifStatement', self.indent, True)


    def compileExpression(self):
        '''
        term (op term)*
        '''
        writeStruct(self.outs, 'expression', self.indent)
        self.indent += 1
        self.compileTerm()
        while True:
            if self.nextTokenIsValue(SYM_ADD) or self.nextTokenIsValue(SYM_SUB) \
                    or self.nextTokenIsValue(SYM_MUL) or self.nextTokenIsValue(SYM_DIV) \
                    or self.nextTokenIsValue(SYM_AND) or self.nextTokenIsValue(SYM_OR) \
                    or self.nextTokenIsValue(SYM_LT) or self.nextTokenIsValue(SYM_GT) \
                    or self.nextTokenIsValue(SYM_EQ):
                _, op = self.match(T_SYMBOL)
                self.compileTerm()
                # write the vm code for the operator
                self.vmwriter.writeArithmetic(op)
            else:
                break
        self.indent -= 1
        writeStruct(self.outs, 'expression', self.indent, True)


    def compileTerm(self):
        '''
        integerConstant | stringConstant | keywordConstant | varName | varName '[' Expression ']'
        | subroutineCall | '(' expression ')' | unaryOp term
        '''
        writeStruct(self.outs, 'term', self.indent)
        self.indent += 1

        # leading unary op
        if self.nextTokenIsValue(SYM_SUB) or self.nextTokenIsValue(SYM_NOT):
            _, op = self.match(T_SYMBOL)
            self.compileTerm()
            self.vmwriter.writeArithmetic(op, unary=True)

        else: # no leading unary op
            if self.nextTokenIsType(T_INT_CONST):
                _, numConst = self.match(T_INT_CONST)
                # write out the vm code
                self.vmwriter.writePush(M_CONSTANT, numConst)

            elif self.nextTokenIsType(T_STRING_CONST):
                _, strConst = self.match(T_STRING_CONST)
                # write out the vm code
                # string constant is dealt as a series of constant push
                # and with the builtin String class.
                strConst = strConst[1: -1] # get rid of the double quotes
                # create the string object with its length as parameter
                self.vmwriter.writePush(M_CONSTANT, len(strConst))
                self.vmwriter.writeCall('String.new', 1)
                for c in strConst:
                    self.vmwriter.writePush(M_CONSTANT, ord(c))
                    self.vmwriter.writeCall('String.appendChar', 2)

            elif self.nextTokenIsType(T_KEYWORD):
                _, kwConst = self.match(T_KEYWORD, [KW_TRUE, KW_FALSE, KW_NULL, KW_THIS])
                # write out the vm code, true = -1, false, null = 0, this = pointer 0
                if kwConst == KW_TRUE: # true is done by push 0 and bitwise not
                    self.vmwriter.writePush(M_CONSTANT, 0)
                    self.vmwriter.writeArithmetic(SYM_NOT)
                elif kwConst in [KW_FALSE, KW_NULL]:
                    self.vmwriter.writePush(M_CONSTANT, 0)
                else: # KW_THIS
                    self.vmwriter.writePush(M_POINTER, 0)

            # simple variable or array element or subroutine call
            elif self.nextTokenIsType(T_IDENTIFIER):

                _, name = self.match(T_IDENTIFIER)
                kind = self.symtab.kindOf(name)
                index = self.symtab.indexOf(name)
                # array element
                if self.nextTokenIsValue(SYM_L_BRACKET): 
                    self.match(T_SYMBOL, SYM_L_BRACKET)
                    self.compileExpression()
                    self.match(T_SYMBOL, SYM_R_BRACKET)
                    # write out vm code
                    # get the correct element address
                    self.vmwriter.writePush(self.getSegementOfKind(kind), index)
                    self.vmwriter.writeArithmetic(SYM_ADD)
                    self.vmwriter.writePop(M_POINTER, 1)
                    self.vmwriter.writePush(M_THAT, 0)

                # subroutine call
                elif self.nextTokenIsValue(SYM_DOT) or self.nextTokenIsValue(SYM_L_PAREN):
                    self.compileSubroutineCall(name)

                # simple variable
                else:
                    self.vmwriter.writePush(self.getSegementOfKind(kind), index)

            # (expression)
            elif self.nextTokenIsValue(SYM_L_PAREN):
                self.match(T_SYMBOL, SYM_L_PAREN)
                self.compileExpression()
                self.match(T_SYMBOL, SYM_R_PAREN)

        self.indent -= 1
        writeStruct(self.outs, 'term', self.indent, True)


    def compileExpressionList(self):
        nArgs = 0
        writeStruct(self.outs, 'expressionList', self.indent)
        self.indent += 1
        # check if empty expression list
        if not self.nextTokenIsValue(SYM_R_PAREN):
            self.compileExpression()
            nArgs += 1
            while self.nextTokenIsValue(SYM_COMMA):
                self.match(T_SYMBOL, SYM_COMMA)
                self.compileExpression()
                nArgs += 1
        self.indent -= 1
        writeStruct(self.outs, 'expressionList', self.indent, True)
        return nArgs


    def compileSubroutineCall(self, name):
        '''
        Parse for either a class function call or a simple function call.
        '''
        nArgs = 0
        if self.nextTokenIsValue(SYM_DOT): # class function call
            self.match(T_SYMBOL, SYM_DOT)
            _, dot_name = self.match(T_IDENTIFIER)
            # check the subroutine for object.method or class.function
            if self.symtab.kindOf(name): # object.method
                kind = self.symtab.kindOf(name)
                index = self.symtab.indexOf(name)
                # For object, we use its class name as part of the function name.
                # Not the object variable name. The object is passed as the hidden
                # first argument to the call.
                type = self.symtab.typeOf(name)
                name = type
                self.vmwriter.writePush(self.getSegementOfKind(kind), index) # push the object as hidden argument
                nArgs = 1
            name = name + '.' + dot_name
        else: # a simple function call can only be a method call within its own class
            name = self.className + '.' + name
            self.vmwriter.writePush(M_POINTER, 0) # object (this) as hidden argument
            nArgs = 1

        self.match(T_SYMBOL, SYM_L_PAREN)
        nArgs += self.compileExpressionList()
        self.match(T_SYMBOL, SYM_R_PAREN)

        self.vmwriter.writeCall(name, nArgs)


    def close(self):
        self.outs.close()


# Type of tokens
T_WHITE           = 'white'
T_COMMENT         = 'comment'
T_KEYWORD         = 'keyword'
T_SYMBOL          = 'symbol'
T_IDENTIFIER      = 'identifier'
T_INT_CONST       = 'integerConstant'
T_STRING_CONST    = 'stringConstant'

# detailed token tags
KW_CLASS = 'class'
KW_CONSTRUCTOR = 'constructor'
KW_FUNCTION = 'function'
KW_METHOD = 'method'
KW_FIELD = 'field'
KW_STATIC = 'static'
KW_VAR = 'var'
KW_INT = 'int'
KW_CHAR = 'char'
KW_BOOLEAN = 'boolean'
KW_VOID = 'void'
KW_TRUE = 'true'
KW_FALSE = 'false'
KW_NULL = 'null'
KW_THIS = 'this'
KW_LET = 'let'
KW_DO = 'do'
KW_IF = 'if'
KW_ELSE = 'else'
KW_WHILE = 'while'
KW_RETURN = 'return'

SYM_L_CURLY = '{'
SYM_R_CURLY = '}'
SYM_L_PAREN = '('
SYM_R_PAREN = ')'
SYM_L_BRACKET = '['
SYM_R_BRACKET = ']'
SYM_DOT = '.'
SYM_COMMA = ','
SYM_SEMICOLON = ';'
SYM_ADD = '+'
SYM_SUB = '-'
SYM_MUL = '*'
SYM_DIV = '/'
SYM_AND = '&'
SYM_OR = '|'
SYM_LT = '<'
SYM_GT = '>'
SYM_EQ = '='
SYM_NOT = '~'

pattern_recognizer = [
    (re.compile(r'[\t\r\n ]+'),         T_WHITE),
    (re.compile(r'//.*'),               T_COMMENT),
    (re.compile(r'/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/'),      T_COMMENT),
    (re.compile(r'class\b|constructor\b|function\b|method\b|field\b|static\b|var\b|int\b|char\b|boolean\b|void\b|true\b|false\b|null\b|this\b|let\b|do\b|if\b|else\b|while\b|return\b'), T_KEYWORD),
    (re.compile(r'\{|\}|\(|\)|\[|\]|\.|,|;|\+|-|\*|/|&|\||<|>|=|~'), T_SYMBOL),
    (re.compile(r'[0-9]+'), T_INT_CONST),
    (re.compile(r'\"[^\"]*\"'), T_STRING_CONST),
    (re.compile(r'[A-Za-z_][A-Za-z0-9_]*'), T_IDENTIFIER),
]

class JackTokenizer(object):

    def __init__(self, fileStub):
        f = open(fileStub + '.jack')
        self.iStream = f.read()
        f.close()
        self.outs = open(fileStub + 'T.xml', 'w')
        writeStruct(self.outs, 'tokens', 0)
        self.pos = 0 # position in the iStream
        # The currently matched token value and type
        self.cur_type = None # i.e. token type
        self.cur_value = None

    def hasMoreTokens(self):
        return True if self.pos <= len(self.iStream)-1 else False

    def advance(self):
        '''
        Read next token from the stream and set it as the current token.
        '''
        # Loop through the patterns to find a match
        while self.hasMoreTokens():
            matched = None
            for regex, tType in pattern_recognizer:
                matched = regex.match(self.iStream, self.pos)
                if matched: # if something is matched
                    tValue = matched.group(0)
                    self.pos += len(tValue)
                    if tType == T_WHITE or tType == T_COMMENT: # ignore white/comments
                        break
                    # Set for the correct tType and tValue
                    self.cur_type = tType
                    self.cur_value = tValue
                    writeToken(self.outs, self.cur_type, self.cur_value)
                    return True
            if matched is None:
                sys.stderr.write('Unrecognized charater: ' + self.iStream[self.pos] + '\n')
                sys.exit(1)
            # if we reach here thats because we got a white

        # if we reach here, we are at the end of the stream
        self.cur_type = None
        self.cur_value = None
        return False


    def tokenType(self):
        return self.cur_type

    def keyword(self):
        return self.cur_value

    def symbol(self):
        return self.cur_value

    def identifier(self):
        return self.cur_value

    def intVal(self):
        return int(self.cur_value)

    def stringVal(self):
        return self.cur_value[1:-1] # strip the double quotes

    def match(self, tType, tValue=None):
        '''
        Match the current token against the given token type and value.
        Report error if not match.
        '''
        # Check for the end of file
        if self.cur_type is None and self.cur_value is None:
            sys.stderr.write('End of file deteced. Expected token type: ' 
                    + str(tType) + '\n')
            sys.exit(1)

        # Trying to match multiple token types
        if type(tType) != list:
            tType = [tType]
        if self.cur_type not in tType:
            sys.stderr.write('Expected token type: ' + str(tType) + '\n')
            sys.exit(1)

        # Trying to match multiple token values
        if tValue:
            if type(tValue) != list:
                tValue = [tValue]
            if self.cur_value not in tValue:
                sys.stderr.write('Expected token value: ' + str(tValue) + '\n')
                sys.exit(1)

        # The actual matched type and value
        tType = self.cur_type
        tValue = self.cur_value

        # Everything is matched for the current token, so get the next token
        self.advance() 

        # debug print
        # print tType, ' - ', tValue

        # The actual type and value matched
        return tType, tValue

    def close(self):
        writeStruct(self.outs, 'tokens', 0, True)
        self.outs.close()


def usage(prog):
    sys.stderr.write('usage: %s [filename]\n' % prog)
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
            if file.endswith(".jack"):
                filelist.append(file)

    # process files
    for file in filelist:
        fileStub = file[0:file.rindex('.')]
        tokenizer = JackTokenizer(fileStub)
        symtab = SymbolTable()
        vmwriter = VMWriter(fileStub)
        compiler = CompilationEngine(fileStub, tokenizer, symtab, vmwriter)

        # start parsing from the top class
        compiler.compileClass()

        # wrap up files
        tokenizer.close()
        vmwriter.close()
        compiler.close()

        #print symtab.class_scope
        #print symtab.sub_scope

