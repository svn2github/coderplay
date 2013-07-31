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
    
    outs = open(filepath('token.i',root=srcdir), 'w')

    keys = __tagDict.keys()
    keys.sort()

    for key in keys:
        if key == 271 or key == 301:
            outs.write('\n');
        line = '#define %-15s %d\n' % (__tagDict[key], key)
        outs.write(line)

    outs.close()

