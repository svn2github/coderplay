import sys
import re

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
                # begining of "pos" of the text. This feature is critical
                # to the lexer. It is similar to the function of the 
                # lookahead character.
                match = token_type[2].match(text, pos)
                if match:
                    matched_text = match.group(0)
                    matched_length = len(matched_text)
                    matched_tag = token_type[1]
                    break
            if not match:
                raise LexError('Illegal character', 
                        text[pos], oneline.line_number, pos+1)
            else:
                if matched_tag != 0:
                    tokens.append((matched_text, matched_tag))
                pos += matched_length
        return tokens

class LexError(Exception):
    pass

if __name__ == '__main__':
    import specs, file
    lexer = Lexer()
    for token_type in specs.token_type_list:
        lexer.add_token_type(token_type)

    line = file.Line('a = 1+2+3  s = "abc" if')
    tokens = lexer(line)
    print tokens


