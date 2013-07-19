from lexer.lexer import Lexer

ins = open('../tests/lexer_test/1.em')
lex = Lexer(ins.read())
ins.close()

while True:
    token = lex.getToken()
    if token is None:
        break
    print '%-10s line %3d' % (token, lex.line)


