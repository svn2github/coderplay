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
                | empty_stmt
                
compound_stmt ::=
            if_stmt
                | while_stmt
                | for_stmt

stmt_list ::=
            simple_stmt (empty_stmt simple_stmt)* [empty_stmt]

statement ::=
            stmt_list <EOL> | compound_stmt

file_input ::=
            (<EOL> | statement)*
'''

def is_addop(token):
    return 1 if token.tag in [EPW_OP_ADD, EPW_OP_SUB] else 0


def is_mulop(token):
    return 1 if token.tag in [EPW_OP_MUL, EPW_OP_DIV] else 0


def is_number(token):
    return 1 if token.tag in [EPW_OP_INT, EPW_OP_FLOAT] else 0


# The starting point for parsing a file input
def parse_file(tokenlist):

    while pos < len(tokenlist):
        # This is the same as the lookahead token
        token = tokenlist.get()

        if token.tag == EPW_OP_EOL:
            tokenlist.match(EPW_OP_EOL)
        else:
            parse_statement(tokenlist)
    

def parse_statement(tokenlist):

    token = tokenlist.get()
        
    if token.tag in [EPW_KW_IF, EPW_KW_WHILE, EPW_KW_FOR]:
        parse_compound_stmt(tokenlist)
    else:
        parse_stmt_list(tokenlist)
        tokenlist.match(EPW_OP_EOL)


def parse_compound_stmt(tokenlist):
    pass


def parse_stmt_list(tokenlist):

    # the first simple stmt
    parse_simple_stmt(tokenlist)

    # Match the 0 or more (empty_stmt simple_stmt)
    # This also matches the optional semicolon at the end
    while tokenlist.get().tag == EPW_OP_SEMICOLON:
        parse_empty_stmt(tokenlist)
        if tokenlist.has_more():
            parse_simple_stmt(tokenlist)
        else:
            break


def parse_empty_stmt(tokenlist):

    tokenlist.match(EPW_OP_SEMICOLON)
    # match any consecutive semicolons
    while tokenlist.get().tag == EPW_OP_SEMICOLON:
        tokenlist.match(EPW_OP_SEMICOLON)

def parse_simple_stmt(tokenlist):

    token = tokenlist.get()

    if token.tag == EPW_KW_PRINT:
        parse_print_stmt(tokenlist)

    elif token.tag in [EPW_INT, EPW_FLOAT]:
        parse_expression(tokenlist)

    elif token.tag == EPW_OP_SEMICOLON:
        parse_empty_stmt(tokenlist)

    else:
        # if the next token is a "=", it is an assignment
        token = tokenlist.get(pos+1)
        if token.tag == EPW_OP_ASSIGN:
            parse_assign_stmt(tokenlist)
        else:
            parse_expression(tokenlist)


def parse_print_stmt(tokenlist):
    pass


def parse_expression(tokenlist):

    parse_term(tokenlist)

    while is_addop(tokenlist.get()):
        parse_addop(tokenlist)
        parse_term(tokenlist)


def parse_term(tokenlist):
    parse_factor(tokenlist)

    while is_mulop(tokenlist.get()):
        parse_mulop(tokenlist)
        parse_factor(tokenlist)

def parse_factor(tokenlist):

    token = tokenlist.get()

    if is_number(token):
        parse_number(tokenlist)

    elif token.tag == EPW_OP_L_PAREN:
        tokenlist.match(EPW_OP_L_PAREN)
        parse_expression(tokenlist)
        tokenlist.match(EPW_OP_R_PAREN)

    else:
        parse_variable(tokenlist)

def parse_assign_stmt(tokenlist):
    pass






