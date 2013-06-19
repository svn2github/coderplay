import re

'''
The specification of Emma language
'''

# Token Type
EPW_WHITE           = 'WHITE'
EPW_COMMENT         = 'WHITE'

EPW_KW_IF           = 'IF'
EPW_KW_ELSE         = 'ELSE'
EPW_KW_WHILE        = 'WHILE'
EPW_KW_FOR          = 'FOR'
EPW_KW_DEF          = 'DEF'
EPW_KW_PRINT        = 'PRINT'
EPW_KW_CONTINUE     = 'CONTINUE'
EPW_KW_BREAK        = 'BREAK'
EPW_KW_RETURN       = 'RETURN'

EPW_OP_ADD          = '+'
EPW_OP_SUB          = '-'
EPW_OP_MUL          = '*'
EPW_OP_DIV          = '/'
EPW_OP_MOD          = '%'
EPW_OP_L_PAREN      = '('
EPW_OP_R_PAREN      = ')'
EPW_OP_ASSIGN       = '='
EPW_OP_EOL          = 'EOL'
EPW_OP_COLON        = ':'
EPW_OP_SEMICOLON    = ';'
EPW_OP_COMMA        = ','
EPW_OP_L_CURLY      = '{'
EPW_OP_R_CURLY      = '}'
EPW_OP_L_BRACKET    = '['
EPW_OP_R_BRACKET    = ']'
EPW_OP_GT           = '>'
EPW_OP_LT           = '<'
EPW_OP_GE           = '>='
EPW_OP_LE           = '<='
EPW_OP_EQ           = '=='
EPW_OP_NE           = '!='
EPW_OP_AND          = 'and'
EPW_OP_OR           = 'or'
EPW_OP_XOR          = 'xor'
EPW_OP_NOT          = 'not'

EPW_INT             = 'INT'
EPW_FLOAT           = 'FLOAT'
EPW_STR             = 'STR'
EPW_ID              = 'ID'

# The order of the token_type_list does matter. Keyword should be positioned
# before ID, otherwise ID would match every keywords. It is not necessary to
# manually count for the match of the maximum length. If we order the 
# patterns properly in the list, it can naturally distinguish keywords with
# the same prefix. For an example, "end" and "endfor", "endfor" should be 
# positioned before "end". So the lexer tries to match "endfor" first and
# thus avoid the situation where an "endfor" is partially matched by an "end".
# The order of the list works in a similar way to the greedy match of the FLEX
# regular expressions.
token_type_list = [
    (r'[\t ]+',     EPW_WHITE),
    (r'#[^\n]*',    EPW_COMMENT),
    # Operators
    # 2 charactar matches
    (r'>=',         EPW_OP_GE),
    (r'<=',         EPW_OP_LE),
    (r'==',         EPW_OP_EQ),
    (r'!=',         EPW_OP_NE),
    # 1 charactor matches
    (r'\+',         EPW_OP_ADD),
    (r'-',          EPW_OP_SUB),
    (r'\*',         EPW_OP_MUL),
    (r'/',          EPW_OP_DIV),
    (r'%',          EPW_OP_MOD),
    (r'\(',         EPW_OP_L_PAREN),
    (r'\)',         EPW_OP_R_PAREN),
    (r'\{',         EPW_OP_L_CURLY),
    (r'\}',         EPW_OP_R_CURLY),
    (r'\[',         EPW_OP_L_BRACKET),
    (r'\]',         EPW_OP_R_BRACKET),
    (r'=',          EPW_OP_ASSIGN),
    (r'\n',         EPW_OP_EOL),
    (r';',          EPW_OP_SEMICOLON),
    (r':',          EPW_OP_COLON),
    (r',',          EPW_OP_COMMA),
    (r'>',          EPW_OP_GT),
    (r'<',          EPW_OP_LT),
    (r'\band\b',        EPW_OP_AND),
    (r'\bor\b',         EPW_OP_OR),
    (r'\bxor\b',        EPW_OP_XOR),
    (r'\bnot\b',        EPW_OP_NOT),

    (r'\bif\b',         EPW_KW_IF),
    (r'\belse\b',       EPW_KW_ELSE),
    (r'\bwhile\b',      EPW_KW_WHILE),
    (r'\bfor\b',        EPW_KW_FOR),
    (r'\bdef\b',        EPW_KW_DEF),
    (r'\bprint\b',      EPW_KW_PRINT),
    (r'\bcontinue\b',   EPW_KW_CONTINUE),
    (r'\bbreak\b',      EPW_KW_BREAK),
    (r'\breturn\b',      EPW_KW_RETURN),

    (r'[0-9]+\.[0-9]*',         EPW_FLOAT),
    (r'[0-9]*\.[0-9]+',         EPW_FLOAT),
    (r'[0-9]+',     EPW_INT),
    (r'\"[^\"]*\"',             EPW_STR),
    (r'\'[^\']*\'',             EPW_STR),
    (r'[A-Za-z_][A-Za-z0-9_]*', EPW_ID),
]

regex_func                  = re.compile(r'ID \( [^\)]*\)')
regex_var_slice             = re.compile(r'ID \[ [^\]]*\]')
regex_func_slice            = re.compile(r'ID \( [^\)]*\) \[ [^\]]*\]')

regex_var_slice_assign      = re.compile(r'ID \[ [^\]]*\] =')
regex_func_slice_assign     = re.compile(r'ID \( [^\)]*\) \[ [^\]]*\] =')
# ID L_BRACKET ((?!R_BRACKET).)* R_BRACKET ASSIGN

SETTINGS = [
    ('$DEBUG', 1), 
    ('$NAME', 'Emma'),
    ('$PROMPT', 'In'),
    ('$PROMPT_CONTINUE', '.'),
    ('$SHIFTWIDTH', 4), 
    ('$VERSION', '0.1.0'), 
    ('$MOTD', ['Emma Peiran Wang says Hi!', 
               'No!',
               'More, Please.',
               'Mine!',
               'Me!',
               'Sit.',
               'Bunny, Bunny ...',
               'Meow Meow ...',
              ]),
]

