import sys, os
import re






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

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer # input
        self.className = self.tokenizer.fileStub
        self.outs = open(self.className + '.xml', 'w')
        self.indent = 0

    def match(self, tType, tValue=None):
        '''
        Match and write a token
        '''
        tType, tValue = self.tokenizer.match(tType, tValue)
        writeToken(self.outs, tType, tValue, self.indent)

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

        # start parsing 
        writeStruct(self.outs, 'classVarDec', self.indent)
        self.indent += 1
        self.match(T_KEYWORD, [KW_STATIC, KW_FIELD]) # static, field
        # type | className
        if self.nextTokenIsType(T_KEYWORD):
            self.match(T_KEYWORD, [KW_INT, KW_CHAR, KW_BOOLEAN])
        else:
            self.match(T_IDENTIFIER)
        self.match(T_IDENTIFIER) # varName

        while self.nextTokenIsValue(SYM_COMMA): # (',' varName)* 
            self.match(T_SYMBOL, SYM_COMMA)
            self.match(T_IDENTIFIER)

        # End of class variable declaration
        self.match(T_SYMBOL, SYM_SEMICOLON) # ';'
        # closing
        self.indent -= 1
        writeStruct(self.outs, 'classVarDec', self.indent, True)

    def compileSubroutine(self):
        writeStruct(self.outs, 'subroutineDec', self.indent)
        self.indent += 1
        self.match(T_KEYWORD, [KW_CONSTRUCTOR, KW_FUNCTION, KW_METHOD])
        if self.nextTokenIsType(T_KEYWORD):
            self.match(T_KEYWORD, [KW_VOID, KW_INT, KW_CHAR, KW_BOOLEAN])
        else:
            self.match(T_IDENTIFIER)
        self.match(T_IDENTIFIER) # subroutineName
        self.match(T_SYMBOL, SYM_L_PAREN)
        self.compileParameterList() # parameter list
        self.match(T_SYMBOL, SYM_R_PAREN)
        # subroutine body
        self.compileSubroutineBody()
        # closing
        self.indent -= 1
        writeStruct(self.outs, 'subroutineDec', self.indent, True)

    def compileParameterList(self):
        writeStruct(self.outs, 'parameterList', self.indent)
        self.indent += 1
        # check if empty parameter list
        if not self.nextTokenIsValue(SYM_R_PAREN):
            # type
            if self.nextTokenIsType(T_KEYWORD):
                self.match(T_KEYWORD, [KW_INT, KW_CHAR, KW_BOOLEAN])
            else:
                self.match(T_IDENTIFIER)
            self.match(T_IDENTIFIER) # varName
            while self.nextTokenIsValue(SYM_COMMA):
                self.match(T_SYMBOL, SYM_COMMA) # ',' type varName
                if self.nextTokenIsType(T_KEYWORD):
                    self.match(T_KEYWORD, [KW_INT, KW_CHAR, KW_BOOLEAN])
                else:
                    self.match(T_IDENTIFIER)
                self.match(T_IDENTIFIER)
        self.indent -= 1
        writeStruct(self.outs, 'parameterList', self.indent, True)


    def compileSubroutineBody(self):
        writeStruct(self.outs, 'subroutineBody', self.indent)
        self.indent += 1
        self.match(T_SYMBOL, SYM_L_CURLY)
        while self.nextTokenIsValue(KW_VAR):
            self.compileVarDec()
        self.compileStatements()
        self.match(T_SYMBOL, SYM_R_CURLY)
        self.indent -= 1
        writeStruct(self.outs, 'subroutineBody', self.indent, True)


    def compileVarDec(self):
        writeStruct(self.outs, 'varDec', self.indent)
        self.indent += 1
        self.match(T_KEYWORD, KW_VAR) # 'var'
        # type
        if self.nextTokenIsType(T_KEYWORD):
            self.match(T_KEYWORD, [KW_INT, KW_CHAR, KW_BOOLEAN])
        else:
            self.match(T_IDENTIFIER)
        self.match(T_IDENTIFIER) # varName
        while self.nextTokenIsValue(SYM_COMMA):
            self.match(T_SYMBOL, SYM_COMMA) # ',' varName
            self.match(T_IDENTIFIER)
        self.match(T_SYMBOL, SYM_SEMICOLON)
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
        self.match(T_IDENTIFIER) # class or function name
        self.compileSubroutineCall()
        self.match(T_SYMBOL, SYM_SEMICOLON)
        self.indent -= 1
        writeStruct(self.outs, 'doStatement', self.indent, True)


    def compileLet(self):
        writeStruct(self.outs, 'letStatement', self.indent)
        self.indent += 1
        self.match(T_KEYWORD, KW_LET)
        self.match(T_IDENTIFIER)
        if self.nextTokenIsValue(SYM_L_BRACKET): # array element
            self.match(T_SYMBOL, SYM_L_BRACKET)
            self.compileExpression()
            self.match(T_SYMBOL, SYM_R_BRACKET)
        self.match(T_SYMBOL, SYM_EUQAL)
        self.compileExpression()
        self.match(T_SYMBOL, SYM_SEMICOLON)
        self.indent -= 1
        writeStruct(self.outs, 'letStatement', self.indent, True)


    def compileWhile(self):
        writeStruct(self.outs, 'whileStatement', self.indent)
        self.indent += 1
        self.match(T_KEYWORD, KW_WHILE)
        self.match(T_SYMBOL, SYM_L_PAREN)
        self.compileExpression()
        self.match(T_SYMBOL, SYM_R_PAREN)
        self.match(T_SYMBOL, SYM_L_CURLY)
        self.compileStatements()
        self.match(T_SYMBOL, SYM_R_CURLY)
        self.indent -= 1
        writeStruct(self.outs, 'whileStatement', self.indent, True)


    def compileReturn(self):
        writeStruct(self.outs, 'returnStatement', self.indent)
        self.indent += 1
        self.match(T_KEYWORD, KW_RETURN)
        if not self.nextTokenIsValue(SYM_SEMICOLON):
            self.compileExpression()
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
        self.match(T_SYMBOL, SYM_L_CURLY)
        self.compileStatements()
        self.match(T_SYMBOL, SYM_R_CURLY)
        if self.nextTokenIsValue(KW_ELSE):
            self.match(T_KEYWORD, KW_ELSE)
            self.match(T_SYMBOL, SYM_L_CURLY)
            self.compileStatements()
            self.match(T_SYMBOL, SYM_R_CURLY)
        self.indent -= 1
        writeStruct(self.outs, 'ifStatement', self.indent, True)


    def compileExpression(self):
        writeStruct(self.outs, 'expression', self.indent)
        self.indent += 1
        self.compileTerm()
        while True:
            if self.nextTokenIsValue(SYM_ADD) or self.nextTokenIsValue(SYM_SUB) \
                    or self.nextTokenIsValue(SYM_MUL) or self.nextTokenIsValue(SYM_DIV) \
                    or self.nextTokenIsValue(SYM_AND) or self.nextTokenIsValue(SYM_OR) \
                    or self.nextTokenIsValue(SYM_LT) or self.nextTokenIsValue(SYM_GT) \
                    or self.nextTokenIsValue(SYM_EUQAL):
                self.match(T_SYMBOL)
                self.compileTerm()
            else:
                break
        self.indent -= 1
        writeStruct(self.outs, 'expression', self.indent, True)


    def compileTerm(self):
        writeStruct(self.outs, 'term', self.indent)
        self.indent += 1

        # leading unary op
        if self.nextTokenIsValue(SYM_SUB) or self.nextTokenIsValue(SYM_NOT):
            self.match(T_SYMBOL)
            self.compileTerm()

        else: # no leading unary op
            if self.nextTokenIsType(T_INT_CONST):
                self.match(T_INT_CONST)
            elif self.nextTokenIsType(T_STRING_CONST):
                self.match(T_STRING_CONST)
            elif self.nextTokenIsType(T_KEYWORD):
                self.match(T_KEYWORD, [KW_TRUE, KW_FALSE, KW_NULL, KW_THIS])
            elif self.nextTokenIsType(T_IDENTIFIER):
                self.match(T_IDENTIFIER)
                if self.nextTokenIsValue(SYM_L_BRACKET): # array element
                    self.match(T_SYMBOL, SYM_L_BRACKET)
                    self.compileExpression()
                    self.match(T_SYMBOL, SYM_R_BRACKET)
                elif self.nextTokenIsValue(SYM_DOT) or self.nextTokenIsValue(SYM_L_PAREN): # class.method or function
                    self.compileSubroutineCall()
            elif self.nextTokenIsValue(SYM_L_PAREN): # (expression)
                self.match(T_SYMBOL, SYM_L_PAREN)
                self.compileExpression()
                self.match(T_SYMBOL, SYM_R_PAREN)

        self.indent -= 1
        writeStruct(self.outs, 'term', self.indent, True)


    def compileExpressionList(self):
        writeStruct(self.outs, 'expressionList', self.indent)
        self.indent += 1
        # check if empty expression list
        if not self.nextTokenIsValue(SYM_R_PAREN):
            self.compileExpression()
            while self.nextTokenIsValue(SYM_COMMA):
                self.match(T_SYMBOL, SYM_COMMA)
                self.compileExpression()
        self.indent -= 1
        writeStruct(self.outs, 'expressionList', self.indent, True)


    def compileSubroutineCall(self):
        '''
        Parse for either a class.method call or a simple function call.
        '''
        if self.nextTokenIsValue(SYM_DOT): # class.method
            self.match(T_SYMBOL, SYM_DOT)
            self.match(T_IDENTIFIER)
        self.match(T_SYMBOL, SYM_L_PAREN)
        self.compileExpressionList()
        self.match(T_SYMBOL, SYM_R_PAREN)


    def close(self):
        self.outs.close()


T_WHITE           = 'white'
T_COMMENT         = 'comment'
T_KEYWORD         = 'keyword'
T_SYMBOL          = 'symbol'
T_IDENTIFIER      = 'identifier'
T_INT_CONST       = 'integerConstant'
T_STRING_CONST    = 'stringConstant'

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
SYM_EUQAL = '='
SYM_NOT = '~'

pattern_recognizer = [
    (re.compile(r'[\t\r\n ]+'),         T_WHITE),
    (re.compile(r'//.*'),               T_COMMENT),
    (re.compile(r'/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/'),      T_COMMENT),
    (re.compile(r'class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return'), T_KEYWORD),
    (re.compile(r'\{|\}|\(|\)|\[|\]|\.|,|;|\+|-|\*|/|&|\||<|>|=|~'), T_SYMBOL),
    (re.compile(r'[0-9]+'), T_INT_CONST),
    (re.compile(r'\"[^\"]*\"'), T_STRING_CONST),
    (re.compile(r'[A-Za-z_][A-Za-z0-9_]*'), T_IDENTIFIER),
]

class JackTokenizer(object):

    def __init__(self, infile):
        f = open(infile)
        self.iStream = f.read()
        f.close()
        self.fileStub = infile[0:infile.rindex('.')]
        self.outs = open(self.fileStub + 'T.xml', 'w')
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

        print tType, ' - ', tValue

        # Everything is matched for the current token, so get the next token
        self.advance() 

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
        tokenizer = JackTokenizer(file)
        compiler = CompilationEngine(tokenizer)

        # start parsing from the top class
        compiler.compileClass()

        # wrap up files
        tokenizer.close()
        compiler.close()

