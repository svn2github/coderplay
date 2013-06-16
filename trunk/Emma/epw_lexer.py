import sys
import re
from specs import *
from epw_parser import ParseError, set_ContinueInput


class Token():
    def __init__(self, value, tag):
        self.value = value
        self.tag = tag

    def __nonzero__(self):
        if (self.value is not None) and (self.tag is not None):
            return 1
        else:
            return 0

    def __repr__(self):
        return '(' + repr(self.value) + ', ' + repr(self.tag) + ')'


class TokenList():
    def __init__(self):
        self.tlist = []
        self.pos = 0

    def append(self, token):
        self.tlist.append(token)

    def get(self, offset=0):
        pos = self.pos + offset
        if pos >= 0 and pos < len(self): 
            return self.tlist[pos]
        else:
            # out of boundary
            return Token(None, None)

    def has_more(self):
        return self.pos < len(self)

    def is_last(self):
        return self.pos == len(self)-1

    def match(self, tag_to_match):
        cur_token = self.get()
        if cur_token.tag == tag_to_match:
            self.pos += 1
        else:
            # If the cur_token is None, that means we are at the end of
            # of the input stream and we may want ask for more input
            # instead of throwing an error. If it is not None, we want
            # stop the contiuation. "if cur_token" return 1 if the token
            # is not None and return 0 if it is None.
            if cur_token:
                set_ContinueInput(0)
            raise ParseError('Expected', tag_to_match)
        return cur_token

    def __repr__(self):
        ret = [repr(t) for t in self.tlist]
        if len(ret):
            if self.pos >=0 and self.pos < len(ret):
                ret[self.pos] = '-->' + ret[self.pos] + '<--'
            else:
                ret.append('--> <--')
        return '[' + ', '.join(ret) + ']'

    def __len__(self):
        return len(self.tlist)

class Lexer():
    def __init__(self):
        self.token_type_list = []

    def add_token_type(self, token_type):
        pattern, tag = token_type
        regex = re.compile(pattern)
        self.token_type_list.append((pattern, tag, regex))

    def __call__(self, oneline):
        text = oneline.text
        tokenlist = TokenList()
        pos = 0
        while pos < len(text):
            for token_type in self.token_type_list:
                # Note that the regex.match matches the pattern from the 
                # begining of "pos" of the text. This feature is critical
                # to the lexer. It is similar to the function of the 
                # lookahead character.
                match = token_type[2].match(text, pos)
                if match:
                    matched_text = match.group(0)
                    matched_tag = token_type[1]
                    break
            if not match:
                raise LexError('Illegal character', 
                        text[pos], oneline.line_number, pos+1)
            else:
                if matched_tag != 'WHITE':
                    tokenlist.append(Token(matched_text, matched_tag))
                pos += len(matched_text)
        return tokenlist

class LexError(Exception):
    pass

if __name__ == '__main__':
    import specs, file
    lexer = Lexer()
    for token_type in specs.token_type_list:
        lexer.add_token_type(token_type)

    line = file.Line('a = 1+2+3  s = "abc" if')
    tokenlist = lexer(line)
    print tokenlist


