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
EPW_KW_PRINT        = 'PRINT'

EPW_OP_ADD          = '+'
EPW_OP_SUB          = '-'
EPW_OP_MUL          = '*'
EPW_OP_DIV          = '/'
EPW_OP_L_PAREN      = '('
EPW_OP_R_PAREN      = ')'
EPW_OP_ASSIGN       = '='
EPW_OP_EOL          = 'EOL'
EPW_OP_SEMICOLON    = ';'
EPW_OP_L_CURLY      = '{'
EPW_OP_R_CURLY      = '}'

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
    (r'\+',         EPW_OP_ADD),
    (r'-',          EPW_OP_SUB),
    (r'\*',         EPW_OP_MUL),
    (r'/',          EPW_OP_DIV),
    (r'\(',         EPW_OP_L_PAREN),
    (r'\)',         EPW_OP_R_PAREN),
    (r'\{',         EPW_OP_L_CURLY),
    (r'\}',         EPW_OP_R_CURLY),
    (r'=',          EPW_OP_ASSIGN),
    (r'\n',         EPW_OP_EOL),
    (r';',          EPW_OP_SEMICOLON),
    (r'if',         EPW_KW_IF),
    (r'else',       EPW_KW_ELSE),
    (r'while',      EPW_KW_WHILE),
    (r'for',        EPW_KW_FOR),
    (r'print',      EPW_KW_PRINT),
    (r'[0-9]+',     EPW_INT),
    (r'[0-9]+\.[0-9]*',         EPW_FLOAT),
    (r'[0-9]*\.[0-9]+',         EPW_FLOAT),
    (r'\"[^\"]*\"',             EPW_STR),
    (r'\'[^\"]*\'',             EPW_STR),
    (r'[A-Za-z_][A-Za-z0-9_]*', EPW_ID),
]

