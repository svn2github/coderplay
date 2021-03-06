import sys
import re
from specs import *
from epw_parser import ParseError
from epw_env import get_topenv


class Token():
    def __init__(self, value, tag, pos):
        self.value = value
        self.tag = tag
        self.pos = pos

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
        self.nLCurly = 0
        self.nRCurly = 0

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

    def reset(self):
        self.tlist = []
        self.pos = 0
        self.nLCurly = 0
        self.nRCurly = 0

    def append(self, token):
        self.tlist.append(token)

    def concatenate(self, anotherList):
        if len(anotherList) > 0:
            self.tlist.extend(anotherList.tlist)
            self.nLCurly += anotherList.nLCurly
            self.nRCurly += anotherList.nRCurly

    def get(self, offset=0):
        pos = self.pos + offset
        if pos >= 0 and pos < len(self): 
            return self.tlist[pos]
        else:
            # out of boundary
            return Token(None, None, None)

    def get_rest_line(self):
        # Get all tokens that forms an unit (before breaking by terminators etc.)
        rest = []
        offset = 0
        while self.get(offset).tag not in [EPW_OP_EOL, EPW_OP_SEMICOLON, EPW_OP_L_CURLY, None]:
            rest.append(self.get(offset).tag)
            offset += 1
        return ' '.join(rest)

    def has_more(self):
        return self.pos < len(self)

    def is_last(self):
        return self.pos == len(self)-1

    def match(self, tag_to_match):
        cur_token = self.get()
        if cur_token.tag == tag_to_match:
            self.pos += 1
        else:
            raise ParseError('Expected: ' + tag_to_match, 
                    get_topenv().get('$INPUT_LINES').get_content_around_pos(cur_token.pos))
        return cur_token

class Lexer():
    def __init__(self):
        self.token_type_list = []

    def add_token_type(self, token_type):
        pattern, tag = token_type
        regex = re.compile(pattern)
        self.token_type_list.append((pattern, tag, regex))

    def __call__(self, lines):
        text = lines.text
        tokenlist = TokenList()
        pos = lines.pos
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
                lineno = lines.get_lineno(pos)
                raise LexError('Illegal character: ' + text[pos],
                        lines.get_content_around_pos(pos))
            else:
                if matched_tag != 'WHITE':
                    tokenlist.append(Token(matched_text, matched_tag, pos))
                    if matched_tag == EPW_OP_L_CURLY:
                        tokenlist.nLCurly += 1
                    elif matched_tag == EPW_OP_R_CURLY:
                        tokenlist.nRCurly += 1
                pos += len(matched_text)
        # update the lexed position
        lines.pos = pos
        return tokenlist

class LexError(Exception):
    def __repr__(self):
        return '%%[LexError] %s\n%s' % self.args

if __name__ == '__main__':
    import specs, file
    lexer = Lexer()
    for token_type in specs.token_type_list:
        lexer.add_token_type(token_type)

    line = file.Line('a = 1+2+3  s = "abc" if')
    tokenlist = lexer(line)
    print tokenlist


