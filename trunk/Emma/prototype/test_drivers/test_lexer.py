import sys
import os
import filecmp
import lexer.tag as Tag
from lexer.lexer import Lexer, LexError

script = os.path.realpath(__file__)
fields = script.split(os.path.sep)[0:-3]
fields.append('tests')
fields.append('lexer_test')
testdir = os.path.sep.join(fields)
filelist = [file for file in os.listdir(testdir) if file.endswith('.em')]

# Pass a "cmp" command line argument to make the script generate the compare files
suffix = '.cmp' if len(sys.argv)>1 and sys.argv[1] == 'cmp' else '.out'

for file in filelist:

    infile = testdir + os.path.sep + file
    outfile = infile[0:-3] + suffix
    ins = open(infile)
    lex = Lexer(ins.read())
    ins.close()

    outs = open(outfile, 'w')

    #print 'Test:', file

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

    outs.write(outstr_1)
    outs.write('\n')
    outs.write(outstr_2)
    outs.close()

    #print outstr_1
    #print outstr_2

    # only compare ot compare files if we are doing output
    if suffix == '.out':
        cmpfile = infile[0:-3] + '.cmp'
        if filecmp.cmp(outfile, cmpfile):
            print '%-20s: PASS' % file
        else:
            print '%-20s: FAIL' % file

