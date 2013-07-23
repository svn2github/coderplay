import sys
import lexer.tag as Tag
from lexer.lexer import Lexer, LexError

ins = open('../tests/lexer_test/test1.em')
lex = Lexer(ins.read())
ins.close()

outstr_1 = ''
outstr_2 = ''

# set last token to EOL so we can skip the first EOL if it is
# from the end of a comment
lastTokenTag = '\n'

while True:

    try:
        token = lex.getToken(lastTokenTag)
    except LexError as e:
        print e
        sys.exit(0)

    # the line and col number of the token
    line = lex.line
    col = lex.col

    # If no more token, it is finished
    if token is None:
        break

    # Keep track of the last token
    lastTokenTag = token.tag

    # Two outputs
    out = str(token)
    outstr_1 += out
    if out != '\n':
        outstr_1 += ' '

    tag = token.tag
    if isinstance(tag, str):
        tag = ord(tag)
    out = Tag.tag2str(tag)
    outstr_2 += out
    if out != '\n':
        outstr_2 += ' '


print outstr_1
print
print outstr_2

