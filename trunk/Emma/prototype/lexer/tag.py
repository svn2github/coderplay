'''
Tags for tokens (starts from 256 to avoid conflict against ASCII code)
'''

# Keywords
PRINT       = 256
IF          = 257
ELIF        = 258
ELSE        = 259
WHILE       = 260
FOR         = 261
CONTINUE    = 262
BREAK       = 263
DEF         = 264
RETURN      = 265
NULL        = 266
CLASS       = 267
AND         = 268
OR          = 269
NOT         = 270
IMPORT      = 271
PACKAGE     = 272
TRY         = 273
RAISE       = 274
CATCH       = 275
FINALLY     = 276
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

