import sys
from lexer.lexer import Lexer

ins = open('../tests/lexer_test/test1.em')
lex = Lexer(ins.read())
ins.close()

outstr_1 = ''
outstr_2 = ''

# set last token to EOL so we can skip the first EOL if it is
# from the end of a comment
lastTokenTag = '\n'
while True:
    token = lex.getToken(lastTokenTag)
    # the line and col number of the token
    line = lex.line
    col = lex.col
    if token is None:
        break
    lastTokenTag = token.tag
    out = str(token)
    outstr_1 += out
    if out != '\n':
        outstr_1 += ' '

    out = token.tagStr()
    outstr_2 += out
    if out != '\n':
        outstr_2 += ' '


print outstr_1
print
print outstr_2
