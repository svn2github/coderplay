import sys
from lexer.lexer import Lexer

ins = open('../tests/lexer_test/1.em')
lex = Lexer(ins.read())
ins.close()

outstr_1 = ''
outstr_2 = ''

lastTokenTag = -1
while True:
    token = lex.getToken(lastTokenTag)
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