import sys
import tag as Tag
from utils.utils import filepath, srcdir

class Token(object):
    '''A token is what returned from a lexer everytime it is called. A basic
    token has only a tag field of integer type. This basic type is to be
    used for any single character tokens and the character's Ascii code
    is used as the tag.'''

    def __init__(self, tag):
        self.tag = tag

    def __repr__(self):
        return str(self.tag)

    def tagStr(self):
        if self.tag == '\n':
            return str(self.tag)
        else:
            return repr(self.tag)


class Word(Token):
    '''A word is a token with a string of multiple character. These include
    identifiers and keywords as well as any other language units longer
    than one character, e.g. >=, <=, == etc.
    The tag number is manually defined in tag module and the actual
    string of the token is set as its lexeme.'''

    def __init__(self, lexeme, tag):
        super(Word, self).__init__(tag)
        self.lexeme = lexeme

    def __repr__(self):
        return self.lexeme

    def tagStr(self):
        return repr(self.tag)


# Multiple character word tokens that are not identifiers or keywords
W_dstar   = Word('**', Tag.DSTAR)
W_le      = Word('<=', Tag.LE)
W_eq      = Word('==', Tag.EQ)
W_ge      = Word('>=', Tag.GE)
W_ne      = Word('!=', Tag.NE)
    

class Integer(Token):
    '''A integer number token. The tag number is defined in tag module
    and the other field is the actual value of this number'''

    def __init__(self, value):
        super(Integer, self).__init__(Tag.INTEGER)
        self.value = value

    def __repr__(self):
        return str(self.value)

    def tagStr(self):
        return repr(self.tag)


class Float(Token):
    '''A float number token. The tag number is defined in tag module
    and the other field is the actual value of this number'''

    def __init__(self, value):
        super(Float, self).__init__(Tag.FLOAT)
        self.value = value

    def __repr__(self):
        return str(self.value)

    def tagStr(self):
        return repr(self.tag)

class String(Token):
    '''A string literal token. The tag number is defined in tag module
    and the other field is the actual string'''

    def __init__(self, s):
        super(String, self).__init__(Tag.STRING)
        self.s = s

    def __repr__(self):
        return str(self.s)

    def tagStr(self):
        return repr(self.tag)


class WordsTable(object):
    '''A hashtable of word type tokens seen in the source program. 
    The word type tokens are only those of identifier and keywords. 
    The table is initialized to have reserved keywords as its entries. 
    Doing so ensure the keywords won't be used as identifiers.'''

    def __init__(self):
        '''Create the hashtable and also reserve the keywords'''
        self.table = {}
        self.reserve(Word('print', Tag.PRINT))
        self.reserve(Word('read', Tag.READ))
        self.reserve(Word('if', Tag.IF))
        self.reserve(Word('elif', Tag.ELIF))
        self.reserve(Word('else', Tag.ELSE))
        self.reserve(Word('while', Tag.WHILE))
        self.reserve(Word('for', Tag.FOR))
        self.reserve(Word('continue', Tag.CONTINUE))
        self.reserve(Word('break', Tag.BREAK))
        self.reserve(Word('def', Tag.DEF))
        self.reserve(Word('return', Tag.RETURN))
        self.reserve(Word('null', Tag.NUL))
        self.reserve(Word('class', Tag.CLASS))
        self.reserve(Word('and', Tag.AND))
        self.reserve(Word('or', Tag.OR))
        self.reserve(Word('xor', Tag.XOR))
        self.reserve(Word('not', Tag.NOT))
        self.reserve(Word('del', Tag.DELETE))
        self.reserve(Word('import', Tag.IMPORT))
        self.reserve(Word('package', Tag.PACKAGE))
        self.reserve(Word('try', Tag.TRY))
        self.reserve(Word('raise', Tag.RAISE))
        self.reserve(Word('catch', Tag.CATCH))
        self.reserve(Word('finally', Tag.FINALLY))

    def reserve(self, token):
        '''Create a entry in the symbol table indexed by a Word token's lexeme.
        For an example, a IF keyword token is created using 'if' as the
        index and the token as its value.'''
        self.table[token.lexeme] = token

    def get(self, key):
        if self.table.has_key(key):
            return self.table[key]
        else:
            return None

    def put(self, key, w):
        self.table[key] = w


class LexError(Exception):
    '''Lexer error'''

    def __str__(self):
        return 'LexError: %s' % self.args


class Lexer(object):
    '''A lexer reads input from a source program and return tokens based on
    the input character stream.'''

    def __init__(self, sbuffer):
        self.words_table = WordsTable()
        self.sbuffer = sbuffer
        self.pos = 0 # the read head position in the input stream
        self.line = 0 # the line number
        self.col = 0 # the colum number
        self.peek = ' ' # important to set as ' '
        self.nulcb = 0 # number of unbalanced left curly bracket
        self.nclass = 0 # number of class definition going on
        self.ndef = 0 # number of function definition going on

    def getc(self):
        '''Simulate the getc function by getting a single character from the
        string buffer at current position. Also advance the position by 1'''
        if self.pos >= 0 and self.pos < len(self.sbuffer):
            self.peek = self.sbuffer[self.pos]
            self.pos += 1
            self.col += 1
        else:
            self.peek = ''

    def matchc(self, c):
        '''Match the given char against the next char. If match, set peek to
        ' ' and return True. We set peek to ' ', so the next call to getToken
        can read the next char by skipping whites.'''
        self.getc()
        if self.peek != c:
            return False
        self.peek = ' ' # this is important
        return True

    def getToken(self, lastTokenTag):
        '''Scan the string buffer and generate a token based on the input
        and lexical rules. 
        Thee lastTokenTag is used to treat consecutive EOL as a single EOL
        and consecutive semicolon as a single semicolon. It is important
        that this argument is provided.
        NOTE there is no need to put a character back to the input stream.
        There are only two possibilities at the end of getToken call.
        1. An extra char is read, e.g. while processing identifier. This
           extra char will be processed next time the function is called.
        2. No extra char is read. In this case, we set peek = ' '. So the
           next call to getToken will effectively skip white and get the
           next non-white char.'''

        # While loop is for treating consecutive EOL and semicolons
        while True:

            # Loop till a non-white character is found
            while self.peek == ' ' or self.peek == '\t':
                self.getc()

            # if we are at the end of input, return None
            if self.peek == '': return None

            # Note the order for processing comment and EOL is important
            # because process EOL also take care of the EOL at the end
            # of a comment.
            # Ignore comments to the end of line
            if self.peek == '#':
                while self.peek != '\n':
                    self.getc()

            # Treat following consecutive EOL as a single EOL. This is twofold. 
            # First, any following consecutive EOL is skipped (but not this EOL).
            # Second, if the last token is also an EOL, this EOL is ignored too.
            #         the while/continue is used for this.
            if self.peek == '\n': 
                while self.peek == '\n':
                    # Count the number of input lines based on EOL
                    self.line += 1
                    # reset colum number for the new line
                    self.col = 0
                    # read pass the EOL
                    self.getc()
                # Only if last token is NOT a EOL
                if lastTokenTag != '\n':
                    return Token('\n')
                else:
                    continue

            # Treat consecutive semicolon as a single one
            # See above EOL treatment for detailed explanation
            if self.peek == ';':
                while self.peek == ';':
                    self.getc()
                # only if last token is NOT a semiclon and NOT a EOL
                if lastTokenTag != ';' and lastTokenTag != '\n':
                    return Token(';')
                else:
                    continue

            # Check if we are having a multi-character symbol
            if self.peek == '>':
                if self.matchc('='):
                    return W_ge
                else:
                    return Token('>')
            elif self.peek == '=':
                if self.matchc('='):
                    return W_eq
                else:
                    return Token('=')
            elif self.peek == '<':
                if self.matchc('='):
                    return W_le
                else:
                    return Token('<')
            elif self.peek == '!':
                if self.matchc('='):
                    return W_ne
                else:
                    return Token('!')
            elif self.peek == '*':
                if self.matchc('*'):
                    return W_dstar
                else:
                    return Token('*')

            # Check if we are having a number 
            if self.peek.isdigit():
                # First try a integer number
                val = 0
                while self.peek.isdigit():
                    val = 10*val + int(self.peek)
                    self.getc()

                # Make sure it is an integer by checking any characters 
                # that make it a float number
                if self.peek != '.' and self.peek != 'e' and self.peek != 'E':
                    return Integer(val)

                else: # otherwise we have a float number
                    # read pass the decimal before process the fraction part
                    if self.peek == '.': self.getc()
                    # Process fraction and generate the float token
                    return self.processFraction(val)

            # Check float numbers start with a dot, i.e. no integer part
            if self.peek == '.':
                # It can be a float only when a digit is following the dot.
                # Note it cannot be 'e' or 'E' because of no integer part
                self.getc()
                if self.peek.isdigit():
                    return self.processFraction(0)
                else:
                    # It is a dot symbol by itself
                    return Token('.')

            # Check if we are having a string literal
            if self.peek == '"' or self.peek == "'":
                if self.peek == '"': 
                    end = '"'
                else:
                    end = "'"
                lastPeek = '\\' # escape the first quote so the while loop works
                s = ''
                while not (self.peek == end and lastPeek != '\\'):
                    s += self.peek 
                    lastPeek = self.peek
                    self.getc()
                s += self.peek # add the ending quote
                self.getc() # read pass through the quote
                return String(s)

            # Check if we are having a identifier/keywords
            if self.peek.isalpha() or self.peek == '_':
                lexeme = ''
                while self.peek.isalnum() or self.peek == '_':
                    lexeme += self.peek
                    self.getc()
                # Check if we have this word in the table already
                # This ensure the keyword is correctly recognized
                w = self.words_table.get(lexeme)
                if w is None:
                    w = Word(lexeme, Tag.IDENT)
                    self.words_table.put(lexeme, w)
                # count the number of class and function definitions
                if w.tag == Tag.CLASS:
                    self.nclass += 1
                    if self.nclass > 1 or self.ndef > 0:
                        self.error('Nested class definition not allowed')
                elif w.tag == Tag.DEF:
                    self.ndef += 1
                    if self.ndef > 1:                        
                        self.error('Nested function definition not allowed')
                # we can now return this word token  
                return w

            # Any character still not recognized is treated as a token of
            # single character.
            token = Token(self.peek)

            # check curly bracket balance
            self.balance()

            # NB: Set peek to ' ', so the next call to getToken can read further
            self.peek = ' '

            return token

    def processFraction(self, intVal):
        '''Process the fraction part of a float number, i.e. digits immediately
        after the demical'''

        # If a fraction part is found e.g. 42.0
        if self.peek.isdigit():
            val = intVal
            d = 10.0 
            # loop for the float number
            while self.peek.isdigit():
                val += int(self.peek)/d
                d *= 10.0
                self.getc()
            # If a scientific notation is found e.g. 42.0E10
            if self.peek != 'e' and self.peek != 'E':
                return Float(val)
            expVal = self.processExponetial()
            val = val * 10.0**expVal
            return Float(val)

        # scientific notation, e.g 4e20, 4.e20
        elif self.peek == 'e' or self.peek == 'E': 
            expVal = self.processExponetial()
            val = intVal * 10.0**expVal
            return Float(val)

        else: # this is only for numbers like 42.
            return Float(intVal*1.0)

    def processExponetial(self):
        '''Process the exponential part (scientific notation) of a float 
        number, e.g. e+10, E-10'''
        val = 0
        self.getc() # read pass e or E
        sign = 1
        if self.peek == '-' or self.peek == '+':
            if self.peek == '-': 
                sign = -1
            self.getc()
        while self.peek.isdigit():
            val = 10*val + int(self.peek)
            self.getc()
        return val*sign

    def balance(self):
        '''Check the balance of curly brackets. Also check if any class or
        function definitions have ended by them. Make sure no nested class
        or function definitions are allowed.'''

        # Record number of unbalanced left curly bracket
        if self.peek == '{':
            self.nulcb += 1

        elif self.peek == '}': # balanced by an right curly bracket
            self.nulcb -= 1
            # Count the number of class and function definitions
            if self.nclass == 1 and self.nulcb == 0:
                self.nclass = 0
            elif self.ndef == 1 and self.nulcb == 0:
                self.ndef = 0
            elif self.nclass == 1 and self.ndef == 1 and self.nulcb == 1:
                self.ndef = 0

            # Something is wrong if we have negative number of unbalanced 
            # left curly bracket
            if self.nulcb < 0:
                self.error('Redundant right curly bracket')

    def error(self, msg):

        # Get text of the line where the error occurs
        text = ''
        # All text till the begining of the line
        pos = self.pos-1
        while self.sbuffer[pos] != '\n':
            text = self.sbuffer[pos] + text
            pos -= 1
        # All text till the end of the line
        pos = self.pos
        while pos < len(self.sbuffer) and self.sbuffer[pos] != '\n':
            text += self.sbuffer[pos]
            pos += 1
        # output the message and report error
        header = 'Near line: %d col %d\n' % (self.line+1, self.col)
        sys.stderr.write(header)
        sys.stderr.write(text+'\n\n')
        raise LexError(msg)

