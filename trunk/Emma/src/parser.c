#include "parser.h"
#include "parser.i"

static int tag;
static Node *ptree;
static jmp_buf __parse_buf;
static char savedLexeme[BUFSIZ];

static int match_token(int t) {
    if (tag == t) {
        tag = get_token(); // get next token
        return 1;
    } else {
        log_error(SYNTAX_ERROR, "unexpected token");
        longjmp(__parse_buf, 1);
    }
}

static int is_r_orop() {
    if (tag == OR)
        return 1;
    else
        return 0;
}

static int is_r_andop() {
    if (tag == AND)
        return 1;
    else
        return 0;
}

static int is_l_op() {
    if (tag == '>' || tag == '<' || tag == GE || tag == LE || tag == EQ
            || tag == NE)
        return 1;
    else
        return 0;
}

static int is_addop() {
    if (tag == '+' || tag == '-')
        return 1;
    else
        return 0;
}

static int is_mulop() {
    if (tag == '*' || tag == '/' || tag == '%')
        return 1;
    else
        return 0;
}

static int is_unary_op() {
    if (tag == '+' || tag == '-')
        return 1;
    else
        return 0;
}

static int is_literal() {
    if (tag == STRING || tag == INTEGER || tag == FLOAT || tag == NUL)
        return 1;
    else
        return 0;
}

Node *parse() {
    if (setjmp(__parse_buf) == 0) {
        // parse the input and generate parse tree
        if (source.type == SOURCE_TYPE_PROMPT) {
            parse_prompt_input();
        } else if (source.type == SOURCE_TYPE_FILE) {
            parse_file_input();
        } else {
            parse_string_input();
        }
    } else {
        printerror();
        freetree(ptree);
        ptree = NULL;
    }
    return ptree;
}

// Forward declaration
static Node * parse_token(Node *, int, char *);

Node *parse_file_input() {
    ptree = newparsetree(FILE_INPUT);
    tag = get_token();
    while (tag != ENDMARK) {
        parse_statement(ptree);
    };
    return ptree;
}

Node *parse_prompt_input() {
    ptree = newparsetree(PROMPT_INPUT);
    tag = get_token();
    /*
     * TODO: We can process magic command here
     */
    parse_statement(ptree);
    return ptree;
}

Node *parse_string_input() {
    ptree = newparsetree(FILE_INPUT);
    tag = get_token();
    while (tag != ENDMARK) {
        parse_statement(ptree);
    };
    return ptree;
}

/*
 * At the end of each parse_xxx, the tag is set to first token
 * of next language struct.
 */
Node *parse_statement(Node *p) {
    Node * n;

    while (tag == EOL) {
        tag = get_token();
    };
    if (tag == ENDMARK)
        return NULL;

    n = addchild(p, STATEMENT, NULL, source.row);

    if (tag == IF || tag == WHILE || tag == FOR || tag == DEF
            || tag == CLASS || tag == TRY) {
        parse_compound_stmt(n);
        match_token(EOL);
    } else {
        parse_simple_stmt(n);
        match_token(EOL);
    }
    return n;
}

Node *parse_simple_stmt(Node *p) {
    Node * n = addchild(p, SIMPLE_STMT, NULL, source.row);
    if (tag == PRINT) {
        parse_print_stmt(n);
    } else if (tag == READ){
        parse_read_stmt(n);
    } else if (tag == CONTINUE) {
        parse_continue_stmt(n);
    } else if (tag == BREAK) {
        parse_break_stmt(n);
    } else if (tag == RETURN) {
        parse_return_stmt(n);
    } else if (tag == PACKAGE) {
        parse_package_stmt(n);
    } else if (tag == IMPORT) {
        parse_import_stmt(n);
    } else if (tag == IDENT) {
        parse_assign_stmt(n); // an expr can be returned instead of an assign_stmt
    } else {
        parse_expr(n);
    }
    return n;
}

Node *parse_print_stmt(Node *p) {
    Node *n = addchild(p, PRINT_STMT, NULL, source.row);
    parse_token(n, PRINT, NULL);
    if (tag == '>') {
        parse_token(n, '>', NULL);
        parse_primary(n);
    }
    parse_expr_list(n);
    return n;
}

Node *parse_read_stmt(Node *p) {
    Node *n = addchild(p, READ_STMT, NULL, source.row);
    parse_token(n, READ, NULL);
    if (tag == '<') {
        parse_token(n, '<', NULL);
        parse_primary(n);
    }
    parse_expr_list(n);
    return n;
}

Node *parse_continue_stmt(Node *p) {
    Node *n = addchild(p, CONTINUE_STMT, NULL, source.row);
    parse_token(n, CONTINUE, NULL);
    return n;
}

Node *parse_break_stmt(Node *p) {
    Node *n = addchild(p, BREAK_STMT, NULL, source.row);
    parse_token(n, BREAK, NULL);
    return n;
}

Node *parse_return_stmt(Node *p) {
    Node *n = addchild(p, RETURN_STMT, NULL, source.row);
    parse_token(n, RETURN, NULL);
    if (tag != EOL) { // optional return value
        parse_expr(n);
    }
    return n;
}

Node *parse_package_stmt(Node *p) {
    Node *n = addchild(p, PACKAGE_STMT, NULL, source.row);
    parse_token(n, PACKAGE, NULL);
    parse_token(n, IDENT, lexeme);
    return n;
}

Node *parse_import_stmt(Node *p) {
    Node *n = addchild(p, IMPORT_STMT, NULL, source.row);
    parse_token(n, IMPORT, NULL);
    parse_token(n, IDENT, lexeme);
    while (tag == '.') {
        parse_token(n, '.', NULL);
        if (tag == '*') {
            parse_token(n, '*', NULL);
            break; // This ensure * is at the end of import
        } else {
            parse_token(n, IDENT, lexeme);
        }
    }
    return n;
}

Node *parse_assign_stmt(Node *p) {
    Node *n = addchild(p, ASSIGN_STMT, NULL, source.row);
    Node *t = parse_target(n);
    if (tag == '=') { // we have an assignment
        if (t->nchildren > 1 && CHILD(t,1)->type == TRAILER) { // we have a trailer
            // Cannot assign to function calls
            if (RCHILD(CHILD(t,1), 0)->type == ')') {
                log_error(SYNTAX_ERROR, "cannot assign to function calls");
                longjmp(__parse_buf, 1);
            }
        }
        parse_token(n, '=', NULL);
        parse_expr(n);
    } else { // it is actually an expression
        n->type = EXPR;
    }
    return n;
}

Node *parse_target(Node *p) {
    Node *n = addchild(p, TARGET, NULL, source.row);
    parse_token(n, IDENT, lexeme);
    parse_trailer(n);
    return n;
}

Node *parse_expr(Node *p) {
    Node *n = addchild(p, EXPR, NULL, source.row);
    parse_r_expr(n);
}

Node *parse_compound_stmt(Node *p) {
    Node *n = addchild(p, COMPOUND_STMT, NULL, source.row);
    if (tag == IF) {
        parse_if_stmt(n);
    } else if (tag == WHILE) {
        parse_while_stmt(n);
    } else if (tag == FOR) {
        parse_for_stmt(n);
    } else if (tag == DEF) {
        //parse_funcdef(n);
    } else if (tag == CLASS) {
        //parse_classdef(n);
    } else { // tag == TRY
        //parse_try_stmt(n);
    }
    return n;
}

Node *parse_if_stmt(Node *p) {
    Node *n = addchild(p, IF_STMT, NULL, source.row);
    parse_token(n, IF, NULL);
    parse_expr(n);
    parse_suite(n);
    while (tag == ELIF) {
        parse_token(n, ELIF, NULL);
        parse_expr(n);
        parse_suite(n);
    }
    if (tag == ELSE) {
        parse_token(n, ELSE, NULL);
        parse_suite(n);
    }
    return n;
}

Node *parse_while_stmt(Node *p) {
    Node *n = addchild(p, WHILE_STMT, NULL, source.row);
    parse_token(n, WHILE, NULL);
    parse_expr(n);
    parse_suite(n);
    return n;
}

Node *parse_for_stmt(Node *p) {
    Node *n = addchild(p, FOR_STMT, NULL, source.row);
    parse_token(n, FOR, NULL);
    parse_token(n, IDENT, lexeme);
    parse_token(n, '=', NULL);
    parse_for_expr(n);
    parse_suite(n);
    return n;
}

Node *parse_for_expr(Node *p) {
    Node *n = addchild(p, FOR_EXPR, NULL, source.row);
    parse_expr(n);
    parse_token(n, ',', NULL);
    parse_expr(n);
    if (tag == ',') {
        parse_token(n, ',', NULL);
        parse_expr(n);
    }
    return n;
}


Node *parse_suite(Node *p) {
    Node *n = addchild(p, SUITE, NULL, source.row);
    if (tag == '{') {
        parse_stmt_block(n);
    } else {
        parse_simple_stmt(n);
    }
    return n;
}

Node *parse_stmt_block(Node *p) {
    Node *n = addchild(p, STMT_BLOCK, NULL, source.row);
    parse_token(n, '{', NULL);
    if (tag == '}') { // So we can have an empty {} pair
        parse_token(n, '}', NULL);
    } else {
        parse_token(n, EOL, NULL);
        while (tag != '}') {
            parse_statement(n);
        }
        parse_token(n, '}', NULL);
    }
    return n;
}


Node *parse_expr_list(Node *p) {
    Node *n = addchild(p, EXPR_LIST, NULL, source.row);
    parse_expr(n);
    while (tag == ',') {
        parse_token(n, tag, NULL);
        parse_expr(n);
    }
    return n;
}

Node *parse_r_expr(Node *p) {
    Node *n = addchild(p, R_EXPR, NULL, source.row);
    parse_r_term(n);
    while (is_r_orop()) {
        parse_token(n, tag, NULL);
        parse_r_term(n);
    }
    return n;
}

Node *parse_r_term(Node *p) {
    Node *n = addchild(p, R_TERM, NULL, source.row);
    parse_r_factor(n);
    while (is_r_andop()) {
        parse_token(n, tag, NULL);
        parse_r_factor(n);
    }
    return n;
}

Node *parse_r_factor(Node *p) {
    Node *n = addchild(p, R_FACTOR, NULL, source.row);
    if (tag == NOT)
        parse_token(n, tag, NULL);
    parse_l_expr(n);
    return n;
}

Node *parse_l_expr(Node *p) {
    Node *n = addchild(p, L_EXPR, NULL, source.row);
    parse_a_expr(n);
    if (is_l_op()) {
        parse_token(n, tag, NULL);
        parse_a_expr(n);
    }
    return n;
}

Node *parse_a_expr(Node *p) {
    Node *n = addchild(p, A_EXPR, NULL, source.row);
    parse_a_term(n);
    if (is_addop()) {
        parse_token(n, tag, NULL);
        parse_a_term(n);
    }
    return n;
}

Node *parse_a_term(Node *p) {
    Node *n = addchild(p, A_TERM, NULL, source.row);
    parse_factor(n);
    if (is_mulop()) {
        parse_token(n, tag, NULL);
        parse_factor(n);
    }
    return n;
}

Node *parse_factor(Node *p) {
    Node *n = addchild(p, FACTOR, NULL, source.row);
    if (is_unary_op()) {
        parse_token(n, tag, NULL);
        parse_factor(n);
    }
    else {
        parse_power(n);
    }
    return n;
}

Node *parse_power(Node *p) {
    Node *n = addchild(p, POWER, NULL, source.row);
    parse_primary(n);
    if (tag == DSTAR) {
        parse_token(n, tag, NULL);
        parse_factor(n);
    }
    return n;
}

Node *parse_primary(Node *p) {
    Node *n = addchild(p, PRIMARY, NULL, source.row);
    parse_atom(n);
    while (tag == '(' || tag == '[' || tag == '.') {
        parse_trailer(n);
    }
    return n;
}

Node *parse_atom(Node *p) {
    Node *n = addchild(p, ATOM, NULL, source.row);
    if (tag == '(') {
        parse_token(n, tag, NULL);
        parse_expr(n);
        parse_token(n, ')', NULL);
    } else if (is_literal()) {
        parse_token(n, tag, lexeme);
    } else {
        parse_token(n, IDENT, lexeme);
    }
    return n;
}

Node *parse_trailer(Node *p) {
    Node *n = NULL;

    while (tag == '(' || tag == '[' || tag == '.') {
        if (n == NULL)
            n = addchild(p, TRAILER, NULL, source.row);

        if (tag == '(') {
            parse_token(n, '(', NULL);
            parse_arglist(n);
            parse_token(n, ')', NULL);
        } else if (tag == '[') {
            parse_token(n, '[', NULL);
            parse_subscription(n);
            parse_token(n, ']', NULL);
        } else if (tag == '.') {
            parse_token(n, '.', NULL);
            parse_token(n, IDENT, lexeme);
        }
    }
    return n;
}



Node *parse_arglist(Node *p) {
    return NULL;
}

Node *parse_subscription(Node *p) {
    return NULL;
}





static Node *
parse_token(Node *p, int token, char *lexeme) {
    // saved the lexeme since match_token changes it
    char *thisLexeme = (lexeme)?strcpy(savedLexeme, lexeme):lexeme;
    match_token(token);
    Node *n = addchild(p, token, thisLexeme, source.row);
    return n;
}


