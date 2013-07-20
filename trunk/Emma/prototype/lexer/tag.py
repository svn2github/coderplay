'''
Tags for tokens (starts from 256 to avoid conflict against ASCII code)
'''

# Keywords
PRINT       = 256
IF          = 257
ELSE        = 258
WHILE       = 259
FOR         = 260
CONTINUE    = 261
BREAK       = 262
DEF         = 263
RETURN      = 264
NULL        = 265
CLASS       = 266
AND         = 267
OR          = 268
NOT         = 269
IMPORT      = 270
PACKAGE     = 271
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

