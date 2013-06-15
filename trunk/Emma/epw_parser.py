from specs import *
from epw_ast import *

'''
Emma Grammer

empty_stmt ::= (";")+

factor = [<unary_op>] ( number 
                        | variable 
                        | "(" expression ")")

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
            simple_stmt (empty_stmt simple_stmt)* [empty_stmt] <EOL>

statement ::=
            stmt_list | compound_stmt

file_input ::=
            (<EOL> | statement)*
'''


def is_addop(token):
    return 1 if token.tag in [EPW_OP_ADD, EPW_OP_SUB] else 0


def is_mulop(token):
    return 1 if token.tag in [EPW_OP_MUL, EPW_OP_DIV] else 0

def is_number(token):
    return 1 if token.tag in [EPW_INT, EPW_FLOAT] else 0


# The starting point for parsing a file input
def parse_file(tokenlist):

    ast_node = Ast_File()

    while tokenlist.has_more():
        # This is the same as the lookahead token
        token = tokenlist.get()

        if token.tag == EPW_OP_EOL:
            tokenlist.match(EPW_OP_EOL)
        else:
            next_node = parse_statement(tokenlist)
            ast_node.append(next_node)

    return ast_node


def parse_statement(tokenlist):

    token = tokenlist.get()
        
    if token.tag in [EPW_KW_IF, EPW_KW_WHILE, EPW_KW_FOR]:
        ast_node = parse_compound_stmt(tokenlist)
    else:
        ast_node = parse_stmt_list(tokenlist)

    return ast_node


def parse_compound_stmt(tokenlist):
    pass


def parse_stmt_list(tokenlist):

    ast_node = Ast_Stmt_List()

    # the first simple stmt
    next_node = parse_simple_stmt(tokenlist)

    ast_node.append(next_node)

    # Match the 0 or more (empty_stmt simple_stmt)
    # This also matches the optional semicolon at the end
    while tokenlist.get().tag == EPW_OP_SEMICOLON:

        next_node = parse_empty_stmt(tokenlist)

        # Parse more simple_stmt if there is still valid token
        # and the token is not a EOL.
        if tokenlist.get().tag != EPW_OP_EOL:
            next_node = parse_simple_stmt(tokenlist)
            if next_node is not None:
                ast_node.append(next_node)
        else:
            break

    tokenlist.match(EPW_OP_EOL)
    return ast_node


def parse_empty_stmt(tokenlist):

    tokenlist.match(EPW_OP_SEMICOLON)
    # match any consecutive semicolons
    while tokenlist.get().tag == EPW_OP_SEMICOLON:
        tokenlist.match(EPW_OP_SEMICOLON)

    return None

def parse_simple_stmt(tokenlist):

    token = tokenlist.get()

    if token.tag == EPW_KW_PRINT:
        ast_node = parse_print_stmt(tokenlist)

    elif token.tag in [EPW_INT, EPW_FLOAT]:
        ast_node = parse_expression(tokenlist)

    elif token.tag == EPW_OP_SEMICOLON:
        ast_node = parse_empty_stmt(tokenlist)

    else:
        # if the next token is a "=", it is an assignment
        token = tokenlist.get(1)
        if token.tag == EPW_OP_ASSIGN:
            ast_node = parse_assign_stmt(tokenlist)
        else:
            ast_node = parse_expression(tokenlist)

    return ast_node


def parse_print_stmt(tokenlist):

    # match the print keyword
    tokenlist.match(EPW_KW_PRINT)
    ast_node = Ast_Print()

    # get the first possible item
    token = tokenlist.get()
    if token.tag == EPW_OP_EOL or token.tag == EPW_OP_SEMICOLON:
        return ast_node

    next_node = parse_expression(tokenlist)
    ast_node.append(next_node)
    token = tokenlist.get()

    while tokenlist.get().tag == EPW_OP_COMMA:
        tokenlist.match(EPW_OP_COMMA)
        next_node = parse_expression(tokenlist)
        ast_node.append(next_node)

    return ast_node

def parse_expression(tokenlist):

    ast_node = parse_term(tokenlist)

    while is_addop(tokenlist.get()):
        op = tokenlist.get().value
        tokenlist.next()
        r_node = parse_term(tokenlist)
        ast_node = Ast_BinAop(op, ast_node, r_node)

    return ast_node


def parse_term(tokenlist):
    ast_node = parse_factor(tokenlist)

    while is_mulop(tokenlist.get()):
        op = tokenlist.get().value
        tokenlist.next()
        r_node = parse_factor(tokenlist)
        ast_node = Ast_BinAop(op, ast_node, r_node)

    return ast_node


def parse_factor(tokenlist):

    token = tokenlist.get()

    # Check if an unary operator exists
    op = None
    if is_addop(token):
        op = token.value
        tokenlist.next()

    if is_number(token):
        ast_node = parse_number(tokenlist)

    elif token.tag == EPW_OP_L_PAREN:
        tokenlist.match(EPW_OP_L_PAREN)
        ast_node = parse_expression(tokenlist)
        tokenlist.match(EPW_OP_R_PAREN)

    else:
        ast_node = parse_variable(tokenlist)

    # package the node with unary operator if exists
    if op:
        ast_node = Ast_UnaryAop(op, ast_node)

    return ast_node


def parse_number(tokenlist):

    token = tokenlist.get()

    if token.tag == EPW_INT:
        ast_node = Ast_Int(int(token.value))
    else:
        ast_node = Ast_Float(float(token.value))

    tokenlist.next()

    return ast_node


def parse_variable(tokenlist):

    token = tokenlist.get()
    ast_node = Ast_Variable(token.value)
    tokenlist.next()
    return ast_node


def parse_assign_stmt(tokenlist):
    pass



