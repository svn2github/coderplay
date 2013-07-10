from specs import *
from epw_env import get_topenv

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

slice ::= ID (arglist | idxlist)* idxlist

arglist ::= "(" [r_expression ("," r_expression)*] ")"

func ::= ID (arglist | idxlist)* arglist

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


# Parse tree node types
PN_LIST         = 0 # list of nodes to be executed in turn
PN_IF           = 1
PN_WHILE        = 2
PN_FOR          = 3
PN_DEF          = 4
PN_CONTINUE     = 5
PN_BREAK        = 6
PN_RETURN       = 7
PN_BRACKET      = 8
PN_PRINT        = 9
PN_VAR          = 10
PN_ASSIGN       = 11
PN_BINOP        = 12
PN_UNARYOP      = 13
PN_INT          = 14
PN_FLOAT        = 15
PN_PAREN        = 16
PN_IDXLIST      = 17
PN_NONE         = 18
PN_ARGLIST      = 19
PN_KWPARM       = 20
PN_STRING       = 21

pn_type_dict = {}
pn_type_dict[PN_LIST] = 'LIST'
pn_type_dict[PN_IF] = 'IF'
pn_type_dict[PN_WHILE] = 'WHILE'
pn_type_dict[PN_FOR] = 'FOR'
pn_type_dict[PN_DEF] = 'DEF'
pn_type_dict[PN_CONTINUE] = 'CONTI'
pn_type_dict[PN_BREAK] = 'BREAK'
pn_type_dict[PN_RETURN] = 'RETURN'
pn_type_dict[PN_BRACKET] = 'BRACKET'
pn_type_dict[PN_PRINT] = 'PRINT'
pn_type_dict[PN_VAR] = 'VAR'
pn_type_dict[PN_ASSIGN] = 'ASSIGN'
pn_type_dict[PN_BINOP] = 'BOP'
pn_type_dict[PN_UNARYOP] = 'UOP'
pn_type_dict[PN_INT] = 'INT'
pn_type_dict[PN_FLOAT] = 'FLOAT'
pn_type_dict[PN_PAREN] = 'PAREN'
pn_type_dict[PN_IDXLIST] = 'IDXLIST'
pn_type_dict[PN_NONE] = 'NONE'
pn_type_dict[PN_ASSIGN] = 'ASSIGN'
pn_type_dict[PN_KWPARM] = 'KWPARM'
pn_type_dict[PN_STRING] = 'STRING'

def pncode2str(code):
    return pn_type_dict[code]


class PT_Node(object):
    ''' A node in the Parse Tree
    '''

    def __init__(self, label=PN_LIST):
        self.label = label
        self.lst = []

    def append(self, item):
        self.lst.append(item)

    def __repr__(self):
        out = pncode2str(self.label) + '['
        if len(self.lst) > 0:
            out += str(self.lst[0])
        for item in self.lst[1:]:
            out += ', '
            out += str(item)
        out += ']'
        return out


# The prompt input is just a single statement
def parse_prompt(tokenlist):
    'The starting point for parsing input from the prompt'
    parsed = parse_statement(tokenlist)
    return parsed


def parse_file(tokenlist):
    'The starting point for parsing a file input'
    # The parsed list holds a tree like structure
    parsed = PT_Node()
    while tokenlist.get(): # this is lookahead token
        subparsed = parse_statement(tokenlist)
        if subparsed: # if it is not None, add to overall parsed list
            parsed.append(subparsed)
    return parsed


def parse_statement(tokenlist):
    'The program is just a bunch of statements'
    token = tokenlist.get()
    # 
    if token.tag == EPW_OP_EOL: # empty line
        tokenlist.match(EPW_OP_EOL)
        return None
    else:
        parsed = parse_stmt_list(tokenlist)
        tokenlist.match(EPW_OP_EOL)
        return parsed


def parse_stmt_block(tokenlist):
    'Parse the stmt_block, i.e. { ... } '
    parsed = PT_Node()
    tokenlist.match(EPW_OP_L_CURLY)
    # if the corresponding "}" if not encountered
    while tokenlist.get().tag != EPW_OP_R_CURLY:
        while tokenlist.get().tag == EPW_OP_EOL:
            tokenlist.match(EPW_OP_EOL)
        if tokenlist.get().tag == EPW_OP_R_CURLY:
            break
        subparsed = parse_stmt_list(tokenlist)
        if subparsed is not None:
            parsed.append(subparsed)
        # check either right curly bracket or EOL for line ending
        if tokenlist.get().tag != EPW_OP_R_CURLY:
            tokenlist.match(EPW_OP_EOL)
        else:
            break
    # match the ending right curly bracket
    tokenlist.match(EPW_OP_R_CURLY)
    return parsed


def parse_stmt_list(tokenlist):
    'A stmt_list is linked using semicolons'
    parsed = PT_Node()
    # Match the first stmt
    if is_compound_keywords(tokenlist.get()):
        subparsed = parse_compound_stmt(tokenlist)
    else:
        subparsed = parse_simple_stmt(tokenlist)
    # in case first stmt is empty
    if subparsed is not None: 
        parsed.append(subparsed)

    # Match following 0 or more stmt
    # This also matches the optional semicolon at the end
    while tokenlist.get().tag == EPW_OP_SEMICOLON:
        parse_empty_stmt(tokenlist)
        # Parse more stmt if the token is not an EOL, which
        # means it is not at the end of the line
        if tokenlist.get().tag not in [EPW_OP_EOL, EPW_OP_R_CURLY]:
            # Match either simple or compound stmts
            if is_compound_keywords(tokenlist.get()):
                subparsed = parse_compound_stmt(tokenlist)
            else:
                subparsed = parse_simple_stmt(tokenlist)
            if subparsed is not None:
                parsed.append(subparsed)
        else:
            break
    return parsed


def parse_compound_stmt(tokenlist):
    'compound_stmt, i.e. if, while, for, def plus {} block'
    token = tokenlist.get()
    if token.tag == EPW_KW_IF:
        parsed = parse_if_stmt(tokenlist)
    elif token.tag == EPW_KW_DEF:
        parsed = parse_def_stmt(tokenlist)
    elif token.tag == EPW_KW_WHILE:
        parsed = parse_while_stmt(tokenlist)
    elif token.tag == EPW_KW_FOR:
        parsed = parse_for_stmt(tokenlist)
    else:
        tokenlist.match('token for a compound_stmt')
    return parsed


def parse_if_stmt(tokenlist):
    'Parse the if_stmt'
    parsed = PT_Node(PN_IF)
    tokenlist.match(EPW_KW_IF)
    # the test
    parsed.append(parse_r_expression(tokenlist))
    # the if part
    if tokenlist.get().tag == EPW_OP_L_CURLY:
        parsed.append(parse_stmt_block(tokenlist))
    else:
        parsed.append(parse_simple_stmt(tokenlist))
    # the optional else part
    if tokenlist.get().tag == EPW_KW_ELSE:
        parsed.append(parse_else_stmt(tokenlist))
    return parsed


def parse_else_stmt(tokenlist):
    'Parse the else_stmt, which can enclose another if_stmt'
    tokenlist.match(EPW_KW_ELSE)
    if tokenlist.get().tag == EPW_OP_L_CURLY:
        parsed = parse_stmt_block(tokenlist)
    elif tokenlist.get().tag == EPW_KW_IF:
        parsed = parse_if_stmt(tokenlist)
    else:
        parsed = parse_simple_stmt(tokenlist)
    return parsed


def parse_while_stmt(tokenlist):
    'Parse the while compound_stmt'
    tokenlist.match(EPW_KW_WHILE)
    parsed = PT_Node(PN_WHILE)
    parsed.append(parse_r_expression(tokenlist))
    if tokenlist.get().tag == EPW_OP_L_CURLY:
        parsed.append(parse_stmt_block(tokenlist))
    else:
        parsed.append(parse_simple_stmt(tokenlist))
    return parsed

def parse_for_stmt(tokenlist):
    'Parse the for loop'
    tokenlist.match(EPW_KW_FOR)
    parsed = PT_Node(PN_FOR)
    # counter
    parsed.append(parse_ID(tokenlist))
    tokenlist.match(EPW_OP_ASSIGN)
    # start
    parsed.append(parse_expression(tokenlist))
    tokenlist.match(EPW_OP_COMMA)
    # end
    parsed.append(parse_expression(tokenlist))
    # The optional step argument
    if tokenlist.get().tag == EPW_OP_COMMA:
        tokenlist.match(EPW_OP_COMMA)
        parsed.append(parse_expression(tokenlist))
    else:
        subparsed = PT_Node(PN_INT)
        subparsed.append(1)
        parsed.append(subparsed) # default step of 1
    # Parse the body
    if tokenlist.get().tag == EPW_OP_L_CURLY:
        parsed.append(parse_stmt_block(tokenlist))
    else:
        parsed.append(parse_simple_stmt(tokenlist))
    return parsed


def parse_def_stmt(tokenlist):
    'Parse the function definition'
    tokenlist.match(EPW_KW_DEF)
    parsed = PT_Node(PN_DEF)
    # function name
    parsed.append(parse_ID(tokenlist))
    # parameter list
    parsed.append(parse_arglist(tokenlist, isdef=1)) 
    # function body
    parsed.append(parse_stmt_block(tokenlist))
    return parsed


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
        parsed = parse_print_stmt(tokenlist)
    elif token.tag == EPW_KW_CONTINUE:
        tokenlist.match(EPW_KW_CONTINUE)
        parsed = PT_Node(PN_CONTINUE)
    elif token.tag == EPW_KW_BREAK:
        tokenlist.match(EPW_KW_BREAK)
        parsed = PT_Node(PN_BREAK)
    elif token.tag == EPW_KW_RETURN:
        tokenlist.match(EPW_KW_RETURN)
        # This parsing may not be optimal though it may works.
        parsed = PT_Node(PN_RETURN)
        if tokenlist.get().tag not in [EPW_OP_EOL, EPW_OP_SEMICOLON, EPW_OP_R_PAREN]:
            parsed.append(parse_r_expression(tokenlist))
    elif token.tag in [EPW_INT, EPW_FLOAT, EPW_STR]:
        parsed = parse_r_expression(tokenlist)
    elif token.tag == EPW_OP_SEMICOLON:
        parsed = parse_empty_stmt(tokenlist)
    elif is_unaryop(token):
        # a leading +/-/not, it can only be an expression 
        parsed = parse_r_expression(tokenlist)

    elif token.tag == EPW_ID:
        # Both ID, slice all start with an ID.
        # If the next token is a "=", it is an assignment with an ID.
        # If it is not, we need to do a regular expression match to 
        # find out whether it is a assignment to a slice.
        # A slice can be either a simple ID with [], ID[], or
        # a function call with [], f()[]

        if tokenlist.get(1).tag == EPW_OP_ASSIGN: # simple case of ID assignment
            parsed = parse_assign_stmt(tokenlist)

        else: # complicate case for possible slice assignment
            rest = tokenlist.get_rest_line()
            # Try to see if we have any function call or slices
            matched = regex_func_slice_mix_assign.match(rest)
            if matched:
                mstring = matched.group(0)
                if mstring[-3] == EPW_OP_R_PAREN:
                    raise ParseError('Cannot Assign to a Function Call', 
                            get_topenv().get('$INPUT_LINES').get_content_around_pos(tokenlist.get().pos))
                parsed = parse_ID(tokenlist)
                for c in mstring:
                    if c == EPW_OP_L_BRACKET:
                        parsed = parse_brackets(tokenlist, parsed)
                    elif c == EPW_OP_L_PAREN:
                        parsed = parse_parenthesis(tokenlist, parsed)
                parsed = parse_assign_stmt(tokenlist, parsed)
            else:
                parsed = parse_r_expression(tokenlist)

    else:
        tokenlist.match('token for a simple_stmt')
    return parsed


def parse_print_stmt(tokenlist):
    'Parse a print_stmt. It can be an empty Print.'
    # match the print keyword
    tokenlist.match(EPW_KW_PRINT)
    parsed = PT_Node(PN_PRINT)
    # get the first possible item
    token = tokenlist.get()
    if token.tag in [EPW_OP_EOL, EPW_OP_SEMICOLON]:
        return parsed
    parsed.append(parse_r_expression(tokenlist))
    token = tokenlist.get()
    # any more following expressions
    while tokenlist.get().tag == EPW_OP_COMMA:
        tokenlist.match(EPW_OP_COMMA)
        parsed.append(parse_r_expression(tokenlist))
    return parsed


def parse_ID(tokenlist):
    token = tokenlist.match(EPW_ID)
    parsed = PT_Node(PN_VAR)
    parsed.append(token.value)
    return parsed

def parse_assign_stmt(tokenlist, left=None):
    'The left operand of assign_stmt can be either an ID or a Function Call'
    parsed = PT_Node(PN_ASSIGN)
    # We need to evaluated for the left operand if it is not given.
    # It must be an ID because a function call would have been given
    # in parse_simple_stmt.
    if left:
        parsed.append(left)
    else:
        parsed.append(parse_ID(tokenlist))
    # The = character
    token = tokenlist.match(EPW_OP_ASSIGN)
    # The right operand
    parsed.append(parse_r_expression(tokenlist))
    return parsed


def parse_r_expression(tokenlist):
    parsed = parse_r_term(tokenlist)
    while is_r_orop(tokenlist.get()):
        subparsed = parsed
        parsed = PT_Node(PN_BINOP)
        parsed.append(subparsed)
        optoken = tokenlist.get()
        tokenlist.match(optoken.tag)
        parsed.append(optoken.value)
        parsed.append(parse_r_term(tokenlist))
    return parsed

def parse_r_term(tokenlist):
    parsed = parse_r_factor(tokenlist)
    while tokenlist.get().value == EPW_OP_AND:
        subparsed = parsed
        parsed = PT_Node(PN_BINOP)
        parsed.append(subparsed)
        optoken = tokenlist.get()
        tokenlist.match(optoken.tag)
        parsed.append(optoken.value)
        parsed.append(parse_r_factor(tokenlist))
    return parsed

def parse_r_factor(tokenlist):
    token = tokenlist.get()
    optoken = None
    if token.tag == EPW_OP_NOT:
        optoken = token
        tokenlist.match(optoken.tag)
    parsed = parse_l_expression(tokenlist)
    if optoken:
        subparsed  = parsed
        parsed = PT_Node(PN_UNARYOP)
        parsed.append(optoken.value)
        parsed.append(subparsed)
    return parsed

def parse_l_expression(tokenlist):
    parsed = parse_l_factor(tokenlist)
    while is_l_op(tokenlist.get()):
        subparsed  = parsed
        parsed = PT_Node(PN_BINOP)
        parsed.append(subparsed)
        optoken = tokenlist.get()
        tokenlist.match(optoken.tag)
        parsed.append(optoken.value)
        parsed.append(parse_l_factor(tokenlist))
    return parsed

def parse_l_factor(tokenlist):
    parsed = parse_expression(tokenlist)
    return parsed

def parse_expression(tokenlist):
    parsed = parse_term(tokenlist)
    while is_addop(tokenlist.get()):
        subparsed  = parsed
        parsed = PT_Node(PN_BINOP)
        parsed.append(subparsed)
        optoken = tokenlist.get()
        tokenlist.match(optoken.tag)
        parsed.append(optoken.value)
        parsed.append(parse_term(tokenlist))
    return parsed

def parse_term(tokenlist):
    parsed = parse_factor(tokenlist)
    while is_mulop(tokenlist.get()):
        subparsed  = parsed
        parsed = PT_Node(PN_BINOP)
        parsed.append(subparsed)
        optoken = tokenlist.get()
        tokenlist.match(optoken.tag)
        parsed.append(optoken.value)
        parsed.append(parse_factor(tokenlist))
    return parsed


def parse_factor(tokenlist):
    'A factor contains any leading unary operator.'
    # Check if an unary operator exists
    token = tokenlist.get()
    optoken = None
    if is_unaryop(token):
        optoken = token
        tokenlist.match(optoken.tag)

    # Parse the factor
    token = tokenlist.get()

    if is_number(token):
        parsed = parse_number(tokenlist)

    elif token.tag == EPW_STR:
        tokenlist.match(EPW_STR)
        # strip the leading and ending quotes
        parsed = PT_Node(PN_STRING)
        parsed.append(token.value[1:-1])

    elif token.tag == EPW_OP_L_PAREN:
        tokenlist.match(EPW_OP_L_PAREN)
        parsed = parse_r_expression(tokenlist)
        tokenlist.match(EPW_OP_R_PAREN)

    elif token.tag == EPW_ID:
        # All of ID, func, slice start with an ID
        rest = tokenlist.get_rest_line()
        # Check if any () or []
        matched = regex_func_slice_mix.match(rest)
        if matched:
            mstring = matched.group(0)
            parsed = parse_ID(tokenlist)
            for c in mstring:
                if c == EPW_OP_L_BRACKET:
                    parsed = parse_brackets(tokenlist, parsed)
                elif c == EPW_OP_L_PAREN:
                    parsed = parse_parenthesis(tokenlist, parsed)
        else:
            parsed = parse_ID(tokenlist)

    else:
        tokenlist.match('token for a factor')

    # package the node with unary operator if exists
    if optoken:
        subparsed  = parsed
        parsed = PT_Node(PN_UNARYOP)
        parsed.append(optoken.value)
        parsed.append(subparsed)

    return parsed


def parse_number(tokenlist):
    token = tokenlist.get()
    if token.tag == EPW_INT:
        tokenlist.match(EPW_INT)
        parsed = PT_Node(PN_INT)
        parsed.append(int(token.value))
    else:
        tokenlist.match(EPW_FLOAT)
        parsed = PT_Node(PN_FLOAT)
        parsed.append(float(token.value))
    return parsed

def parse_brackets(tokenlist, prefix):
    parsed = PT_Node(PN_BRACKET)
    parsed.append(prefix) # ID
    parsed.append(parse_idxlist(tokenlist))
    return parsed

def parse_parenthesis(tokenlist, prefix):
    parsed = PT_Node(PN_PAREN)
    parsed.append(prefix) # function
    parsed.append(parse_arglist(tokenlist))
    return parsed

def parse_idxlist(tokenlist):
    'Parse the idxlist for array like variable'
    parsed = PT_Node(PN_IDXLIST)
    tokenlist.match(EPW_OP_L_BRACKET)
    # The start of the index
    if tokenlist.get().tag != EPW_OP_COLON:
        parsed.append(parse_expression(tokenlist))
    else:
        if tokenlist.get().tag != EPW_OP_COLON:
            raise ParseError('Incorrect index list format',
                    get_topenv().get('$INPUT_LINES').get_content_around_pos(tokenlist.get().pos))
        parsed.append(PT_Node(PN_NONE))
    # The optional end of the index
    if tokenlist.get().tag == EPW_OP_COLON:
        tokenlist.match(EPW_OP_COLON)
        if tokenlist.get().tag not in [EPW_OP_COLON, EPW_OP_R_BRACKET]:
            parsed.append(parse_expression(tokenlist))
        else:
            parsed.append(PT_Node(PN_NONE))
    # The optional step of the index
    if tokenlist.get().tag == EPW_OP_COLON:
        tokenlist.match(EPW_OP_COLON)
        if tokenlist.get().tag != EPW_OP_R_BRACKET:
            parsed.append(parse_expression(tokenlist))
        else:
            parsed.append(PT_Node(PN_NONE))
    tokenlist.match(EPW_OP_R_BRACKET)
    return parsed

def parse_arglist(tokenlist, isdef=0):
    'Parse the argument list, i.e. (a, b, c)'
    parsed = PT_Node(PN_ARGLIST)
    tokenlist.match(EPW_OP_L_PAREN)
    # Parse first argument if it is not empty
    if tokenlist.get().tag != EPW_OP_R_PAREN:
        if isdef:
            subparsed_1 = parse_ID(tokenlist)
        else:
            subparsed_1 = parse_r_expression(tokenlist)
        # Parse possible keyword type parameter
        if tokenlist.get().tag == EPW_OP_ASSIGN:
            pos = tokenlist.match(EPW_OP_ASSIGN).pos
            subparsed_2 = parse_r_expression(tokenlist)
            subparsed = PT_Node(PN_KWPARM)
            subparsed.append(subparsed_1)
            subparsed.append(subparsed_2)
        parsed.append(subparsed)
        # Parse any other following parameters
        while tokenlist.get().tag == EPW_OP_COMMA:
            tokenlist.match(EPW_OP_COMMA)
            if isdef:
                subparsed_1 = parse_ID(tokenlist)
            else:
                subparsed_1 = parse_r_expression(tokenlist)
            # Parse possible keyword type parameter
            if tokenlist.get().tag == EPW_OP_ASSIGN:
                pos = tokenlist.match(EPW_OP_ASSIGN).pos
                subparsed_2 = parse_r_expression(tokenlist)
                subparsed = PT_Node(PN_KWPARM)
                subparsed.append(subparsed_1)
                subparsed.append(subparsed_2)
            parsed.append(subparsed)
    tokenlist.match(EPW_OP_R_PAREN)
    return parsed

class ParseError(Exception):
    def __repr__(self):
        return '%%[ParseError] %s\n%s' % self.args



