import sys, os
import re


def writeToken(outs, tType, tValue, indent=0):
    if tValue == SYM_LT:
        tValue = '&lt;'
    elif tValue == SYM_GT:
        tValue = '&gt;'
    elif tValue == SYM_AND:
        tValue ='&amp;'

    # output to file
    outs('  '*indent + '<' + tType + '> ' + str(tValue) + ' </' + tType + '>\n')


class CompilationEngine(object):

    def __init__(self, tokenizer, outfile):
        self.indent = 0

    def writeStruct(self, struct, close=False):
        self.outs.write('  '*self.indent + '<' 
                + ('/' if close else '') + struct + '>\n')

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

    def compileClass():
        success = self.tokenizer.advance()  # get the 1st token
        if not success:
            return

        # Starting match the class struct
        self.writeStruct('class')
        self.indent += 1

        self.match(T_KEYWORD, KW_CLASS) # match and get next token
        self.match(T_IDENTIFIER)
        self.match(T_SYMBOL, SYM_L_CURLY)

        # Try to figure out what struct comes next
        while True: # variables for the class
            if self.nextTokenIsType(T_KEYWORD) \
                    and self.nextTokenIsValue([KW_STATIC, KW_FIELD]):
                self.compileClassVarDec()
           
        while True: # subroutines for the class
            if self.nextTokenIsType(T_KEYWORD) \
                    and self.nextTokenIsValue([KW_CONSTRUCTOR, KW_FUNCTION, KW_METHOD])
                self.compileSubroutine()

        # End of the class definition
        self.match(T_SYMBOL, SYM_R_CURLY)

        self.indent -= 1
        self.writeStruct('class', True)

    def compileClassVarDec():

        # start parsing 
        self.writeStruct('classVarDec')
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
            self.matched(T_IDENTIFIER)

        # End of class variable declaration
        self.match(T_SYMBOL, SYM_SEMICOLON) # ';'

        self.indent -= 1
        self.writeStruct('classVarDec', True)

    def compileSubroutine():

    def compileParameterList():

    def compileVarDec():

    def compileStatements():

    def compileDo():

    def compileLet():

    def compileWhile():

    def compileReturn():

    def compileIf():

    def compileTerm():

    def compileExpressionList():



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
        outfile = infile[0:infile.rindex('.')] + 'T.xml'
        self.outs = open(outfile, 'w')
        self.outs.write('<tokens>\n')
        self.pos = 0 # position in the iStream
        # The currently matched token value and type
        self.cur_type = None # i.e. token type
        self.cur_value = None

    def hasMoreTokens(self):
        return True if self.pos <= len(self.iStream)-1 else False

    def advance(self):
        if not self.hasMoreTokens():
            self.cur_type = None
            self.cur_value = None
            return False

        for regex, tType in pattern_recognizer:
            matched = regex.match(self.iStream, self.pos)
            if matched: # if something is matched
                tValue = matched.group(0)
                self.pos += len(tValue)
                if tType == T_WHITE or tType == T_COMMENT: # ignore white/comments
                    continue
                # Set for the correct tType and tValue
                self.cur_type, self.cur_value = correctValueByType(tType, tValue)
                writeToken(self.outs, self.cur_type, self.cur_value)
                return True

        sys.stderr.write('Unrecognized charater: ', self.iStream[self.pos] + '\n')
        return False

    def correctValueByType(self, tType, tValue):
        # Set for the correct tType and tValue
        if tType == T_INT_CONST:
            tValue = int(tValue)
        elif tType == T_STRING_CONST: 
            tValue = tValue[1:-1] # strip double quotes
        return tType, tValue

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
        if self.cur_type is None and self.cur_value is None:
            sys.stderr.write('End of file deteced. Expected token type: ' + str(tType) + '\n')

        # Trying to match multiple token types
        if type(tType) != list:
            tType = [tType]
        if self.cur_type not in tType:
            sys.stderr.write('Expected token type: ' + str(tType) + '\n')

        # Trying to match multiple token values
        if tValue:
            if type(tValue) != list:
                tValue = [tValue]
            if self.cur_value not in tValue:
            sys.stderr.write('Expected token value: ' + str(tValue) + '\n')

        tType = self.cur_type
        tValue = self.cur_value

        # Everything is matched for the current token, so get the next token
        self.advance() 

        # The actual type and value matched
        return tType, tValue

    def close(self):
        self.outs.write('</tokens>\n')
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


    for file in filelist:
        tokenizer = JackTokenizer(file)

        while tokenizer.hasMoreTokens():
            tokenizer.advance()



        tokenizer.close()

