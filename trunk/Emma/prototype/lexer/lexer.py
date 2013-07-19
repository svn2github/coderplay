import tag as Tag

class Token(object):
    '''A token is what returned from a lexer everytime it is called. A basic
    token has only a tag field of integer type. This basic type is to be
    used for any single character tokens and the character's Ascii code
    is used as the tag.'''

    def __init__(self, tag):
        self.tag = tag

    def __repr__(self):
        return 'T:' + repr(self.tag)


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
        return 'W' + str(self.tag) + ':' + self.lexeme


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
        return 'I:' + str(self.value)


class Float(Token):
    '''A float number token. The tag number is defined in tag module
    and the other field is the actual value of this number'''

    def __init__(self, value):
        super(Float, self).__init__(Tag.FLOAT)
        self.value = value

    def __repr__(self):
        return 'F:' + str(self.value)


class WordsTable(object):
    '''A hashtable of word type tokens seen in the source program. 
    The word type tokens are only those of identifier and keywords. 
    The table is initialized to have reserved keywords as its entries. 
    Doing so ensure the keywords won't be used as identifiers.'''

    def __init__(self):
        '''Create the hashtable and also reserve the keywords'''
        self.table = {}
        self.reserve(Word('print', Tag.PRINT))
        self.reserve(Word('if', Tag.IF))
        self.reserve(Word('else', Tag.ELSE))
        self.reserve(Word('while', Tag.WHILE))
        self.reserve(Word('for', Tag.FOR))
        self.reserve(Word('continue', Tag.CONTINUE))
        self.reserve(Word('break', Tag.BREAK))
        self.reserve(Word('def', Tag.DEF))
        self.reserve(Word('return', Tag.RETURN))
        self.reserve(Word('null', Tag.NULL))
        self.reserve(Word('class', Tag.CLASS))
        self.reserve(Word('and', Tag.AND))
        self.reserve(Word('or', Tag.OR))
        self.reserve(Word('not', Tag.NOT))

    def reserve(self, token):
        '''Create a entry in the symbol table indexed by a Word token's lexeme.
        For an example, a IF keyword token is created using 'if' as the
        index and the token as its value.'''
        self.table[token.lexeme] = token


class Lexer(object):
    '''A lexer reads input from a source program and return tokens based on
    the input character stream.'''

    def __init__(self, sbuffer):
        self.words_table = WordsTable()
        self.sbuffer = sbuffer
        self.pos = 0
        self.line = 0
        # The lastPeek is used to treat consecutive EOL as a single EOL
        # and consecutive semicolon as a single semicolon
        self.lastPeek = ''

    def getc(self):
        '''Simulate the getc function by getting a single character from the
        string buffer at current position. Also advance the position by 1'''
        if self.pos >= 0 and self.pos < len(self.sbuffer):
            peek = self.sbuffer[self.pos]
            self.pos += 1
        else:
            peek = ''
        return peek

    def ungetc(self):
        '''Simulate the ungetc function that put a character back to the
        input stream. This is done by decrease the position counter by 1.
        This is useful when we need to tell tokens start with the same
        character, e.g. < and <=. If the following character after < does
        not match =, we will put the character back to the stream for 
        future processing.'''
        self.pos -= 1

    def getToken(self):
        '''Scan the string buffer and generate a token based on the input
        and lexical rules'''

        # Loop till a token is found or end of file reached
        while True:

            # get a character from buffer
            peek = self.getc()

            # if we are at the end of input, return None
            if peek == '': return None

            # Ignore white spaces
            if peek == ' ' or peek == '\t': continue

            # Ignore comments to the end of line
            if peek == '#':
                while peek != '\n':
                    self.getc()
                self.line += 1
                continue

            # Count the number of input lines based on EOL
            if peek == '\n': 
                self.line += 1
                # Treat consecutive EOL as a single EOL
                if self.lastPeek == '\n':
                    continue
                else:
                    return Token('\n')

            # Treat consecutive semicolon as one
            if peek == ';':
                if self.lastPeek == ';':
                    continue
                else:
                    return Token(';')

            # Check if we are having a multi-character symbol
            # Note that if the second character does not match, the character
            # needs to be put back to the buffer by ungetc.
            if peek == '>':
                if self.getc() == '=':
                    return W_ge
                else:
                    self.ungetc()
                    return Token(peek)
            elif peek == '=':
                if self.getc() == '=':
                    return W_eq
                else:
                    self.ungetc()
                    return Token(peek)
            elif peek == '<':
                if self.getc() == '=':
                    return W_le
                else:
                    self.ungetc()
                    return Token(peek)
            elif peek == '!':
                if self.getc() == '=':
                    return W_ne
                else:
                    self.ungetc()
                    return Token(peek)
            elif peek == '*':
                if self.getc() == '*':
                    return W_dstar
                else:
                    self.ungetc()
                    return Token(peek)

            # Check if we are having a number 
            if peek.isdigit():
                pass

            # Check if we are having a identifier/keywords
            if peek.isalpha() or peek == '_':
                pass

            
            # update the lastPeek for next call
            self.lastPeek = peek



