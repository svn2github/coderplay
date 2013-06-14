from specs import *

'''
Emma Grammer

empty_stmt ::= (";")+

factor = number | variable | "(" expression ")"

term ::= factor (<mulop> factor)*

expression ::= term (<addop> term)*

simple_stmt ::= 
            expression
                | assign_stmt
                | print_stmt

compound_stmt ::=
            if_stmt
                | while_stmt
                | for_stmt

stmt_list ::=
            [empty_stmt] simple_stmt (empty_stmt simple_stmt)* [empty_stmt]

statement ::=
            stmt_list <EOL> | compound_stmt

file_input ::=
            (<EOL> | statement)*
'''

def match_token(token, tokens, pos):
    token_value, token_tag = tokens[pos]
    if token == token_tag:
        return pos
    else:
        sys.stderr.write("no match\n")
        sys.exit(1)


def parse_file(tokens, pos):

    while pos <= len(tokens):
        # This is the same as the lookahead token
        token_value, token_tag = tokens[pos]

        if token_tag == EPW_OP_EOL:
            pos += 1
        else:
            pos = parse_statement(tokens, pos)
    

def parse_statement(tokens, pos):

    token_value, token_tag = tokens[pos]
        
    if token_tag in [EPW_KW_IF, EPW_KW_WHILE, EPW_KW_FOR]:
        pos = parse_compound_stmt(tokens, pos)
    else:
        pos = parse_stmt_list(tokens, pos)
        pos = match_token('EPW_OP_EOL', tokens, pos)

    return pos


def parse_compound_stmt(tokens, pos):
    pass


def parse_stmt_list(tokens, pos):

    # The optional semicolon at the beginning
    token_value, token_tag = tokens[pos]
    if token_value == EPW_OP_TERMINATOR:
        pos = parse_empty_stmt(tokens, pos)

    # the first simple stmt
    pos = parse_simple_stmt(tokens, pos)

    # This also matches the optional semicolon at the end
    while pos <= len(tokens):
        pos = parse_empty_stmt(tokens, pos)
        if pos <= len(tokens):
            pos = parse_simple_stmt(tokens, pos)
        else:
            break

    return pos


def parse_empty_stmt(tokens, pos):

    token_value, token_tag = tokens[pos]
    pos = match_token(EPW_OP_TERMINATOR, tokens, pos)
    # match any consecutive semicolons
    while pos <= len(tokens):
        token_value, token_tag = tokens[pos]
        if token_tag == EPW_OP_TERMINATOR:
            pos = match_token(EPW_OP_TERMINATOR, tokens, pos)
        else:
            break
    return pos
                

def parse_simple_stmt(tokens, pos):

    token_value, token_tag = tokens[pos]

    if token_tag == EPW_KW_PRINT:
        pos = parse_print_stmt(tokens, pos)
    elif token_tag in [EPW_INT, EPW_FLOAT]:
        pos = parse_expression(tokens, pos)
    else:
        # It must be a expression if it is the last token
        if pos == len(tokens):
            pos = parse_expression(tokens, pos)

        token_value, token_tag = tokens[pos+1]
        if token_tag == EPW_OP_ASSIGN:
            pos = parse_assign_stmt(tokens, pos)
        else:
            pos = parse_expression(tokens, pos)

    return pos


def parse_print_stmt(tokens, pos):
    pass


def parse_expression(tokens, pos):

    pos = parse_term(tokens, pos)

    while pos <= len(tokens):
        pos = parse_addop(tokens, pos)
        if pos <= len(tokens):
            pos = parse_term(tokens, pos)
        else:
            sys.stderr.write("missing operand at the end\n")
            sys.exit(1)



def parse_assign_stmt(tokens, pos):
    pass






