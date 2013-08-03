from utils.utils import filepath, srcdir

'''
Tags for tokens (starts from 256 to avoid conflict against ASCII code)
'''

# Composite operators longer than 1 character
# Single character operators just use its own Ascii code
DSTAR       = 256
LE          = 257
EQ          = 258
GE          = 259
NE          = 260

# Keywords
PRINT       = 271
READ        = 272
IF          = 273
ELIF        = 274
ELSE        = 275
WHILE       = 276
FOR         = 277
CONTINUE    = 278
BREAK       = 279
DEF         = 280
RETURN      = 281
NUL         = 282
CLASS       = 283
AND         = 284
OR          = 285
NOT         = 286
IMPORT      = 287
PACKAGE     = 288
TRY         = 289
RAISE       = 290
CATCH       = 291
FINALLY     = 292
SELF        = 293

# Literals
INTEGER     = 301
FLOAT       = 302
STRING      = 303

#
IDENT       = 304

# Following code to get the name of a tag is only for debug purpose
__tagDict = {}
for k, v in locals().items():
    if not isinstance(v, int): continue
    __tagDict[v] = k

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
        if key == 271 or key == 301:
            outs.write('\n');
        line = '#define %-15s %d\n' % (__tagDict[key], key)
        outs.write(line)

    outs.write('\n#endif\n')
    outs.close()


    outs = open(filepath('lexer.i',root=srcdir), 'w')
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


