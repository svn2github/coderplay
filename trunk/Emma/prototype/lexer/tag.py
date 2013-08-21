from utils.utils import filepath, srcdir

'''
Tags for tokens (starts from 256 to avoid conflict against ASCII code)
'''

# Composite operators longer than 1 character
# Single character operators just use its own Ascii code

token_types = \
'''
DSTAR
LE
EQ
GE
NE

PRINT
READ
IF
ELIF
ELSE
WHILE
FOR
CONTINUE
BREAK
DEF
RETURN
NUL
CLASS
AND
OR
XOR
NOT
DELETE
IMPORT
PACKAGE
TRY
RAISE
CATCH
FINALLY
SELF

INTEGER
FLOAT
STRING
IDENT
'''

token_types = [t for t in token_types.split('\n') if t != '']

for ii in range(len(token_types)):
    locals()[token_types[ii]] = 256 + ii;

# Following code to get the name of a tag is only for debug purpose
__tagDict = {}
for ii in range(len(token_types)):
    __tagDict[ii+256] = token_types[ii]

def tag2str(tag):
    if tag > 255:
        return __tagDict[tag]
    else:
        return chr(tag)

def gen_c_code():
    '''Generate necessary C code from related content in this file.
    '''
    
    outs = open(filepath('token.h',root=srcdir), 'w')

    outs.write('#ifndef _TOKEN_H_\n#define _TOKEN_H_\n\n')
    outs.write('#define %-15s %d\n\n' %('ENDMARK', 0))
    outs.write('#define %-15s %d\n\n' %('EOL', 10))
    outs.write('#define %-15s %d\n' %('CHAR_LF', 10))
    outs.write('#define %-15s %d\n\n' %('CHAR_CR', 13))

    keys = __tagDict.keys()
    keys.sort()

    for key in keys:
        line = '#define %-15s %d\n' % (__tagDict[key], key)
        outs.write(line)

    outs.write('\nextern char *token_types[];\n')
    outs.write('\n#endif\n')
    outs.close()


    outs = open(filepath('lexer.i',root=srcdir), 'w')

    outs.write('char *token_types[] = {\n')
    outs.write('        "%s"' % token_types[0])
    for t in token_types[1:]:
        outs.write(',\n        "%s"' % t)
    outs.write('\n};\n\n')

    outs.write('int match_keyword() {\n')

    from .lexer import WordsTable 
    wtable = WordsTable()

    table = {}
    for k, v in wtable.table.items():
        table[v.tag] = k

    keys = table.keys()
    keys.sort()

    tag = keys[0]
    kw = table[tag]
    text = '    if (strcmp(lexeme, "%s") == 0)\n        return %s;\n' % (kw, tag2str(tag))
    outs.write(text);

    for tag in keys[1:]:
        kw = table[tag]
        text = '    else if (strcmp(lexeme, "%s") == 0)\n        return %s;\n' % (kw, tag2str(tag))
        outs.write(text)

    outs.write('    else\n        return ENDMARK;\n')
    outs.write('}\n')
    outs.close()


