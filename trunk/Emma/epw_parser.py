from specs import *
from epw_ast import *

'''
--------------------------------------------------------------------------------
                                Emma Grammer

    A terminator is to indicate the language construct before it is complete and
can be evaluated. Note that both EOL and Semicolon are terminators. But they 
have following differences:

    1. Semicolon is used for separating statements in a single line.
    2. EOL obviously can only be used at the end of a line.
    3. Semicolon is optional if there no separation for statements in a single
       line. EOL is compulsory to end a line.
    4. A {} pair groups a block of statements, which is tread as a single 
       languague construct. Terminators in between them do not break this single
       construct. NOTE a Terminator is NOT required immediately after the "{" or
       before the "}". It is however still required after the "}" to end the 
       block.
    5. For statements that contains two or more blocks, the ending "}" must be
       in the same line with the following "{", so that the language construct
       is not broken. Using "if {...} else {...} " as an exmaple, the "} else {"
       must be on the same line and no Semicolon terminator in between them 
       either. This behaviour is kind similar to IDL.
    6. Another way to look at the "{" and "}" pair is treat them as "glue" or
       "magnetic" operators. They are glued to each other and take whatever
       statements inside them to become a single languge construct. It is like
       a north and south pair of magnetic poles that attract each other. Note
       that the glue/magnetic only works inside the "{}" pair. Any other 
       language constructs before or after them are not glued. If these other
       language constructs need to be as part of the "{}" language construct.
       They have to be written in the same line. Using "if ... else ..." as an
       example, following statement is a single language construct.
           if x == y {
               do_something()
           } else {
               do_something_else()
           }
       Note how "{" and "}" are glued to each other across multiple lines.

    * Whitespace is insignificant.

--------------------------------------------------------------------------------

mulop :== "*" | "/"
addop :== "+" | "-"
l_op :== ">" | "<" | ">=" | "<=" | "==" | "!="
r_andop :== "and"
r_orop :== "or" | "xor"

factor = [<unary_op>] ( number 
                        | string
                        | ID 
                        | func
                        | slice
                        | "(" r_expression ")")

term ::= factor (<mulop> factor)*

expression ::= term (<addop> term)*

l_factor ::= expression

l_expression ::= l_factor (<l_op> l_factor)*

r_factor ::= [<r_unary_op>] l_expression

r_term ::= r_factor (<r_andop> r_factor)*

r_expression ::= r_term (<r_orop> r_term)*

idxlist ::= "[" [expression] (":" [expression]){0,2} "]"

slice ::= ID [arglist] idxlist

arglist ::= "(" [r_expression ("," r_expression)*] ")"

func ::= ID arglist

assign_stmt ::= (ID | slice) "=" r_expression

print_stmt ::= "print" [r_expression ("," r_expression)*]

empty_stmt ::= (";")+

def_stmt ::= "def" func stmt_block

for_stmt ::= "for" ID "=" expression, expression [, expression] (simple_stmt | stmt_block)

while_stmt ::= "while" r_expression (simple_stmt | stmt_block)

if_stmt ::= "if" r_expression (simple_stmt | stmt_block) [else_stmt] 

else_stmt ::= "else" (if_stmt | simple_stmt | stmt_block)

compound_stmt ::=
            if_stmt
                | while_stmt
                | for_stmt
                | def_stmt

simple_stmt ::= 
            r_expression
                | assign_stmt
                | print_stmt
                | "continue"
                | "break"
                | "return" r_expression
                | empty_stmt

stmt_list ::=
            (simple_stmt | compound_stmt) (empty_stmt (simple_stmt | compound_stmt))* [empty_stmt]

stmt_block ::= "{" (statement)* stmt_list (EOL)* "}" 
                    | "{" (EOL)* "}"

statement ::= EOL | (stmt_list EOL)

file_input ::= (statement)*

prompt_input ::= statement
'''

def is_addop(token):
    return 1 if token.tag in [EPW_OP_ADD, EPW_OP_SUB] else 0

def is_unaryop(token):
    return 1 if token.tag in [EPW_OP_ADD, EPW_OP_SUB, EPW_OP_NOT] else 0

def is_mulop(token):
    return 1 if token.tag in [EPW_OP_MUL, EPW_OP_DIV, EPW_OP_MOD] else 0

def is_r_orop(token):
    return 1 if token.tag in [EPW_OP_OR, EPW_OP_XOR] else 0

def is_l_op(token):
    return 1 if token.tag in [EPW_OP_GT, EPW_OP_LT, EPW_OP_GE, EPW_OP_LE, EPW_OP_EQ, EPW_OP_NE] else 0

def is_compound_keywords(token):
    return 1 if token.tag in [EPW_KW_IF, EPW_KW_WHILE, EPW_KW_FOR, EPW_KW_DEF] else 0

def is_number(token):
    return 1 if token.tag in [EPW_INT, EPW_FLOAT] else 0


def parse_prompt(tokenlist):
    'The starting point for parsing input from the prompt'
    next_node = parse_statement(tokenlist)
    # For empty line, a None is returned implicitly
    if next_node is not None:
        return Ast_Prompt(next_node)


def parse_file(tokenlist):
    'The starting point for parsing a file input'
    ast_node = Ast_File()
    while tokenlist.get(): # this is lookahead token
        next_node = parse_statement(tokenlist)
        if next_node is not None:
            ast_node.append(next_node)
    if len(ast_node): 
        return ast_node


def parse_statement(tokenlist):
    'The program is just a bunch of statements'
    token = tokenlist.get()
    # For empty line, a None is returned implicitly
    if token.tag == EPW_OP_EOL:
        tokenlist.match(EPW_OP_EOL)
    else:
        ast_node = parse_stmt_list(tokenlist)
        tokenlist.match(EPW_OP_EOL)
        return ast_node


def parse_stmt_block(tokenlist):
    'Parse the {} block'
    tokenlist.match(EPW_OP_L_CURLY)
    ast_node = Ast_Stmt_Block()
    # if the corresponding "}" if not encountered
    while tokenlist.get().tag != EPW_OP_R_CURLY:
        while tokenlist.get().tag == EPW_OP_EOL:
            tokenlist.match(EPW_OP_EOL)
        if tokenlist.get().tag == EPW_OP_R_CURLY:
            break
        next_node = parse_stmt_list(tokenlist)
        if next_node is not None:
            ast_node.append(next_node)
        if tokenlist.get().tag != EPW_OP_R_CURLY:
            tokenlist.match(EPW_OP_EOL)
        else:
            break
    tokenlist.match(EPW_OP_R_CURLY)
    return ast_node


def parse_stmt_list(tokenlist):
    'A stmt_list is linked using semicolons'
    ast_node = Ast_Stmt_List()
    # Match the first stmt
    if is_compound_keywords(tokenlist.get()):
        next_node = parse_compound_stmt(tokenlist)
    else:
        next_node = parse_simple_stmt(tokenlist)
    # in case first stmt is empty
    if next_node is not None: 
        ast_node.append(next_node)
    # Match following 0 or more stmt
    # This also matches the optional semicolon at the end
    while tokenlist.get().tag == EPW_OP_SEMICOLON:
        parse_empty_stmt(tokenlist)
        # Parse more stmt if the token is not an EOL, which
        # means it is not at the end of the line
        if tokenlist.get().tag not in [EPW_OP_EOL, EPW_OP_R_CURLY]:
            # Match either simple or compound stmts
            if is_compound_keywords(tokenlist.get()):
                next_node = parse_compound_stmt(tokenlist)
            else:
                next_node = parse_simple_stmt(tokenlist)
            if next_node is not None:
                ast_node.append(next_node)
        else:
            break
    return ast_node


def parse_compound_stmt(tokenlist):
    'if, while, for, def plus {} block'
    token = tokenlist.get()
    if token.tag == EPW_KW_IF:
        ast_node = parse_if_stmt(tokenlist)
    elif token.tag == EPW_KW_DEF:
        ast_node = parse_def_stmt(tokenlist)
    elif token.tag == EPW_KW_WHILE:
        ast_node = parse_while_stmt(tokenlist)
    elif token.tag == EPW_KW_FOR:
        ast_node = parse_for_stmt(tokenlist)
    else:
        tokenlist.match('token for a compound_stmt')
    return ast_node


def parse_if_stmt(tokenlist):
    'Parse the if stmt'
    tokenlist.match(EPW_KW_IF)
    ast_node = Ast_If()
    # the test
    ast_node.predicate = parse_r_expression(tokenlist)
    # the if part
    if tokenlist.get().tag == EPW_OP_L_CURLY:
        ast_node.if_body = parse_stmt_block(tokenlist)
    else:
        ast_node.if_body = parse_simple_stmt(tokenlist)
    # the optional else part
    if tokenlist.get().tag == EPW_KW_ELSE:
        ast_node.else_body = parse_else_stmt(tokenlist)
    return ast_node


def parse_else_stmt(tokenlist):
    'Parse the else_stmt, which can enclose another if_stmt'
    tokenlist.match(EPW_KW_ELSE)
    if tokenlist.get().tag == EPW_OP_L_CURLY:
        ast_node = parse_stmt_block(tokenlist)
    elif tokenlist.get().tag == EPW_KW_IF:
        ast_node = parse_if_stmt(tokenlist)
    else:
        ast_node = parse_simple_stmt(tokenlist)
    return ast_node


def parse_while_stmt(tokenlist):
    'Parse the while compound_stmt'
    tokenlist.match(EPW_KW_WHILE)
    ast_node = Ast_WhileLoop()
    ast_node.predicate = parse_r_expression(tokenlist)
    if tokenlist.get().tag == EPW_OP_L_CURLY:
        ast_node.body = parse_stmt_block(tokenlist)
    else:
        ast_node.body = parse_simple_stmt(tokenlist)
    return ast_node

def parse_for_stmt(tokenlist):
    'Parse the for loop'
    tokenlist.match(EPW_KW_FOR)
    ast_node = Ast_ForLoop()
    ast_node.counter = parse_ID(tokenlist)
    tokenlist.match(EPW_OP_ASSIGN)
    ast_node.start = parse_expression(tokenlist)
    tokenlist.match(EPW_OP_COMMA)
    ast_node.end = parse_expression(tokenlist)
    # The optional step argument
    if tokenlist.get().tag == EPW_OP_COMMA:
        tokenlist.match(EPW_OP_COMMA)
        ast_node.step = parse_expression(tokenlist)
    # Parse the body
    if tokenlist.get().tag == EPW_OP_L_CURLY:
        ast_node.body = parse_stmt_block(tokenlist)
    else:
        ast_node.body = parse_simple_stmt(tokenlist)
    return ast_node


def parse_def_stmt(tokenlist):
    'Parse the function definition'
    tokenlist.match(EPW_KW_DEF)
    ast_node = Ast_DefFunc()
    ast_node.func_name = parse_ID(tokenlist)
    ast_node.parmlist = parse_arglist(tokenlist)
    ast_node.body = parse_stmt_block(tokenlist)
    return ast_node


def parse_empty_stmt(tokenlist):
    'It is 1 or more consecutive semicolons'
    tokenlist.match(EPW_OP_SEMICOLON)
    # match any consecutive semicolons
    while tokenlist.get().tag == EPW_OP_SEMICOLON:
        tokenlist.match(EPW_OP_SEMICOLON)
    return None


def parse_simple_stmt(tokenlist):
    'A simple_stmt is a SINGLE stmt'
    token = tokenlist.get()
    if token.tag == EPW_KW_PRINT:
        ast_node = parse_print_stmt(tokenlist)
    elif token.tag == EPW_KW_CONTINUE:
        tokenlist.match(EPW_KW_CONTINUE)
        ast_node = Ast_Continue()
    elif token.tag == EPW_KW_BREAK:
        tokenlist.match(EPW_KW_BREAK)
        ast_node = Ast_Break()
    elif token.tag == EPW_KW_RETURN:
        tokenlist.match(EPW_KW_RETURN)
        # This parsing may not be optimal though it may works.
        if tokenlist.get().tag not in [EPW_OP_EOL, EPW_OP_SEMICOLON, EPW_OP_R_PAREN]:
            next_node = parse_r_expression(tokenlist)
            ast_node = Ast_Return(next_node)
        else:
            ast_node = Ast_Return()
    elif token.tag in [EPW_INT, EPW_FLOAT, EPW_STR]:
        ast_node = parse_r_expression(tokenlist)
    elif token.tag == EPW_OP_SEMICOLON:
        ast_node = parse_empty_stmt(tokenlist)
    elif is_unaryop(token):
        # a leading +/-/not, it can only be an expression 
        ast_node = parse_r_expression(tokenlist)

    elif token.tag == EPW_ID:
        # Both ID, slice all start with an ID.
        # If the next token is a "=", it is an assignment with an ID.
        # If it is not, we need to do a regular expression match to 
        # find out whether it is a assignment to a slice.
        # A slice can be either a simple ID with [], ID[], or
        # a function call with [], f()[]

        if tokenlist.get(1).tag == EPW_OP_ASSIGN: # simple case of ID assignment
            ast_node = parse_assign_stmt(tokenlist)

        else: # complicate case for possible slice assignment
            rest = tokenlist.get_rest_line()

            if regex_func_slice_assign.match(rest):
                ast_node = parse_assign_stmt(tokenlist, parse_func_slice)
            elif regex_var_slice_assign.match(rest):
                ast_node = parse_assign_stmt(tokenlist, parse_var_slice)
            else:
                ast_node = parse_r_expression(tokenlist)

    else:
        tokenlist.match('token for a simple_stmt')
    return ast_node


def parse_print_stmt(tokenlist):
    'Parse a print_stmt. It can be an empty Print.'
    # match the print keyword
    tokenlist.match(EPW_KW_PRINT)
    ast_node = Ast_Print()
    # get the first possible item
    token = tokenlist.get()
    if token.tag in [EPW_OP_EOL, EPW_OP_SEMICOLON]:
        return ast_node
    next_node = parse_r_expression(tokenlist)
    ast_node.append(next_node)
    token = tokenlist.get()
    # any more following expressions
    while tokenlist.get().tag == EPW_OP_COMMA:
        tokenlist.match(EPW_OP_COMMA)
        next_node = parse_r_expression(tokenlist)
        ast_node.append(next_node)
    return ast_node


def parse_ID(tokenlist):
    token = tokenlist.match(EPW_ID)
    ast_node = Ast_Variable(token.value)
    return ast_node

def parse_assign_stmt(tokenlist, pre_parser=parse_ID):
    'The left operand of assign_stmt can be either an ID or a Function Call'
    # We need to evaluated for the left operand if it is not given.
    # It must be an ID because a function call would have been given
    # in parse_simple_stmt.
    left_operand = pre_parser(tokenlist)
    tokenlist.match(EPW_OP_ASSIGN)
    # The right operand
    next_node = parse_r_expression(tokenlist)
    ast_node = Ast_Assign(left_operand, next_node)
    return ast_node


def parse_r_expression(tokenlist):
    ast_node = parse_r_term(tokenlist)
    while is_r_orop(tokenlist.get()):
        op = tokenlist.get().value
        tokenlist.match(tokenlist.get().tag)
        next_node = parse_r_term(tokenlist)
        ast_node = Ast_BinOp(op, ast_node, next_node)
    return ast_node

def parse_r_term(tokenlist):
    ast_node = parse_r_factor(tokenlist)
    while tokenlist.get().value == EPW_OP_AND:
        op = tokenlist.get().value
        tokenlist.match(tokenlist.get().tag)
        next_node = parse_r_factor(tokenlist)
        ast_node = Ast_BinOp(op, ast_node, next_node)
    return ast_node

def parse_r_factor(tokenlist):
    token = tokenlist.get()
    op = None
    if token.tag == EPW_OP_NOT:
        op = token.value
        tokenlist.match(tokenlist.get().tag)
    ast_node = parse_l_expression(tokenlist)
    if op:
        ast_node = Ast_UnaryOp(op, ast_node)
    return ast_node

def parse_l_expression(tokenlist):
    ast_node = parse_l_factor(tokenlist)
    while is_l_op(tokenlist.get()):
        op = tokenlist.get().value
        tokenlist.match(tokenlist.get().tag)
        next_node = parse_l_factor(tokenlist)
        ast_node = Ast_BinOp(op, ast_node, next_node)
    return ast_node

def parse_l_factor(tokenlist):
    ast_node = parse_expression(tokenlist)
    return ast_node

def parse_expression(tokenlist):
    ast_node = parse_term(tokenlist)
    while is_addop(tokenlist.get()):
        op = tokenlist.get().value
        tokenlist.match(tokenlist.get().tag)
        next_node = parse_term(tokenlist)
        ast_node = Ast_BinOp(op, ast_node, next_node)
    return ast_node

def parse_term(tokenlist):
    ast_node = parse_factor(tokenlist)
    while is_mulop(tokenlist.get()):
        op = tokenlist.get().value
        tokenlist.match(tokenlist.get().tag)
        next_node = parse_factor(tokenlist)
        ast_node = Ast_BinOp(op, ast_node, next_node)
    return ast_node


def parse_factor(tokenlist):
    'A factor contains any leading unary operator.'
    # Check if an unary operator exists
    token = tokenlist.get()
    op = None
    if is_unaryop(token):
        op = token.value
        tokenlist.match(token.tag)

    # Parse the factor
    token = tokenlist.get()

    if is_number(token):
        ast_node = parse_number(tokenlist)

    elif token.tag == EPW_STR:
        tokenlist.match(EPW_STR)
        # strip the leading and ending quotes
        ast_node = Ast_String(token.value[1:-1])

    elif token.tag == EPW_OP_L_PAREN:
        tokenlist.match(EPW_OP_L_PAREN)
        ast_node = parse_r_expression(tokenlist)
        tokenlist.match(EPW_OP_R_PAREN)

    elif token.tag == EPW_ID:
        # All of ID, func, slice start with an ID
        rest = tokenlist.get_rest_line()
        if regex_func_slice.match(rest): # match the longest candidate first
            ast_node = parse_func_slice(tokenlist)
        elif regex_var_slice.match(rest):
            ast_node = parse_var_slice(tokenlist)
        elif regex_func.match(rest):
            ast_node = parse_func_call(tokenlist)
        else:
            ast_node = parse_ID(tokenlist)

    else:
        tokenlist.match('token for a factor')

    # package the node with unary operator if exists
    if op:
        ast_node = Ast_UnaryOp(op, ast_node)

    return ast_node


def parse_number(tokenlist):
    token = tokenlist.get()
    if token.tag == EPW_INT:
        tokenlist.match(EPW_INT)
        ast_node = Ast_Int(int(token.value))
    else:
        tokenlist.match(EPW_FLOAT)
        ast_node = Ast_Float(float(token.value))
    return ast_node

def parse_var_slice(tokenlist):
    'Parse a variable slice'
    ast_node = Ast_Slice()
    ast_node.collection = parse_ID(tokenlist)
    ast_node.idxlist = parse_idxlist(tokenlist)
    return ast_node

def parse_func_slice(tokenlist):
    'Parse a func slice'
    ast_node = Ast_Slice()
    ast_node.collection = parse_func_call(tokenlist)
    ast_node.idxlist = parse_idxlist(tokenlist)
    return ast_node

def parse_idxlist(tokenlist):
    'Parse the idxlist for array like variable'
    ast_node = Ast_IdxList()
    tokenlist.match(EPW_OP_L_BRACKET)
    # The start of the index
    if tokenlist.get().tag != EPW_OP_COLON:
        ast_node.start = parse_expression(tokenlist)
    # The optional end of the index
    if tokenlist.get().tag == EPW_OP_COLON:
        tokenlist.match(EPW_OP_COLON)
        ast_node.nColon += 1
        if tokenlist.get().tag not in [EPW_OP_COLON, EPW_OP_R_BRACKET]:
            ast_node.end = parse_expression(tokenlist)
    # The optional step of the index
    if tokenlist.get().tag == EPW_OP_COLON:
        tokenlist.match(EPW_OP_COLON)
        ast_node.nColon += 1
        if tokenlist.get().tag != EPW_OP_R_BRACKET:
            ast_node.step = parse_expression(tokenlist)
    tokenlist.match(EPW_OP_R_BRACKET)
    return ast_node

def parse_func_call(tokenlist):
    'Parse a function call'
    ast_node = Ast_FuncCall()
    ast_node.func_name = parse_ID(tokenlist)
    ast_node.arglist = parse_arglist(tokenlist)
    return ast_node

def parse_arglist(tokenlist):
    'Parse the argument list, i.e. (a, b, c)'
    ast_node = Ast_ArgList()
    tokenlist.match(EPW_OP_L_PAREN)
    # Parse first argument if it is not empty
    if tokenlist.get().tag != EPW_OP_R_PAREN:
        next_node = parse_r_expression(tokenlist)
        # Parse possible keyword type parameter
        is_kwarg = 0
        if tokenlist.get().tag == EPW_OP_ASSIGN:
            tokenlist.match(EPW_OP_ASSIGN)
            val_node = parse_r_expression(tokenlist)
            next_node = Ast_KeywordParm(next_node, val_node)
            is_kwarg = 1
        ast_node.append(next_node, is_kwarg)
        # Parse any other following parameters
        while tokenlist.get().tag == EPW_OP_COMMA:
            tokenlist.match(EPW_OP_COMMA)
            next_node = parse_r_expression(tokenlist)
            # Parse possible keyword type parameter
            is_kwarg = 0
            if tokenlist.get().tag == EPW_OP_ASSIGN:
                tokenlist.match(EPW_OP_ASSIGN)
                val_node = parse_r_expression(tokenlist)
                next_node = Ast_KeywordParm(next_node, val_node)
                is_kwarg = 1
            ast_node.append(next_node, is_kwarg)
    tokenlist.match(EPW_OP_R_PAREN)
    return ast_node

class ParseError(Exception):
    pass


