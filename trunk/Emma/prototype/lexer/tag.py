'''
Tags for tokens (starts from 256 to avoid conflict against ASCII code)
'''

# Keywords
PRINT       = 256
READ        = 257
IF          = 258
ELIF        = 259
ELSE        = 260
WHILE       = 261
FOR         = 262
CONTINUE    = 263
BREAK       = 264
DEF         = 265
RETURN      = 266
NULL        = 267
CLASS       = 268
AND         = 269
OR          = 270
NOT         = 271
IMPORT      = 272
PACKAGE     = 273
TRY         = 274
RAISE       = 275
CATCH       = 276
FINALLY     = 277
# Operators longer than just 1 character
# Single character operators just use its own Ascii code
DSTAR       = 280
LE          = 281
EQ          = 282
GE          = 283
NE          = 284

# Literals
INTEGER     = 290
FLOAT       = 291
STRING      = 292

#
IDENT       = 300

# Following code to get the name of a tag is only for debug purpose
__tagDict = {}
for k, v in locals().items():
    if k.startswith('__'): continue
    __tagDict[v] = k

def tag2str(tag):
    if tag > 255:
        return __tagDict[tag]
    else:
        return chr(tag)

