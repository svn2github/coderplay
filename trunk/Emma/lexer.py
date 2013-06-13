import sys
import re

class Line():
    def __init__(self, text, line_number=1, filename=None):
        self.text = text
        self.line_number = line_number
        self.filename = filename


class Lexer():
    def __init__(self):
        self.token_type_list = []

    def add_token_type(self, token_type):
        pattern, tag = token_type
        regex = re.compile(pattern)
        self.token_type_list.append((pattern, tag, regex))

    def __call__(self, oneline):
        text = oneline.text
        tokens = []
        pos = 0
        while pos < len(text):
            for token_type in self.token_type_list:
                # Note that the regex.match matches the pattern from the 
                # begining of "pos" of the text. 
                match = token_type[2].match(text, pos)
                if match:
                    matched_text = match.group(0)
                    matched_length = len(matched_text)
                    matched_tag = token_type[1]
                    break
            if not match:
                sys.stderr.write('Illegal character: %s  (L%d, C%d)\n' % (text[pos], oneline.line_number, pos))
                sys.exit(1)
            else:
                if matched_tag is not None:
                    tokens.append((matched_text, matched_tag))
                pos += matched_length
        return tokens


if __name__ == '__main__':
    RESERVED = 'RESERVED'
    INT      = 'INT'
    STR      = 'STR'
    ID       = 'ID'

    # The order of the token_type_list does matter. Keyword should be placed
    # before ID, otherwise ID would match everything. It is not necessary to
    # manually count for the match of the maximum length. If we order the 
    # patterns properly in the list, it can naturally distinguish keywords
    # with same prefix. For an example, end and endfor, "endfor" should be 
    # placed before "end". So the lexer tries to match "endfor" first and
    # thus avoid the situation where an "endfor" is halfly matched by an
    # "end". The order of the list works in a similar way to the greedy match
    # of the FLEX regular expressions.
    token_type_list = [
        (r'[ \n\t]+',              None),
        (r'#[^\n]*',               None),
        (r'\:=',                   RESERVED),
        (r'\(',                    RESERVED),
        (r'\)',                    RESERVED),
        (r';',                     RESERVED),
        (r'\+',                    RESERVED),
        (r'-',                     RESERVED),
        (r'\*',                    RESERVED),
        (r'/',                     RESERVED),
        (r'<',                     RESERVED),
        (r'<=',                    RESERVED),
        (r'>',                     RESERVED),
        (r'>=',                    RESERVED),
        (r'=',                     RESERVED),
        (r'!=',                    RESERVED),
        (r'and',                   RESERVED),
        (r'or',                    RESERVED),
        (r'not',                   RESERVED),
        (r'if',                    RESERVED),
        (r'then',                  RESERVED),
        (r'else',                  RESERVED),
        (r'while',                 RESERVED),
        (r'do',                    RESERVED),
        (r'for',                   RESERVED),
        (r'endfor',                RESERVED),
        (r'end',                   RESERVED),
        (r'\"[^\"]*\"',            STR),
        (r'[0-9]+',                INT),
        (r'[A-Za-z][A-Za-z0-9_]*', ID),
    ]

    lexer = Lexer()
    for token_type in token_type_list:
        lexer.add_token_type(token_type)

    line = Line('and end and do or `1+2+3 "abc" endfor end')
    tokens = lexer(line)
    print tokens


