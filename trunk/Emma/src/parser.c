#include "parser.h"
#include "parser.i"

static int tag;
static Node *ptree;
static jmp_buf __parse_buf;
static char savedLexeme[BUFSIZ];


static match_token_no_advance(int t) {
    if (tag != t) {
        log_error(SYNTAX_ERROR, "unexpected token");
        longjmp(__parse_buf, 1);
    }
}

static match_token(int t) {
    match_token_no_advance(t);
    tag = get_token(); // get next token
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
        // Make sure this line won't be used again in next call
        source.line[0] = '\0';
        source.peek = ' ';
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

static Node *parse_magic_command(Node *p);

Node *parse_prompt_input() {
    int magicCmd;
    ptree = newparsetree(PROMPT_INPUT);
    tag = get_token();
    /*
     * Process magic commands
     */
    if (tag == '.') {
        ptree = parse_magic_command(ptree);
    } else {
        parse_statement(ptree);
    }
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
    } else {
        parse_simple_stmt(n);
    }
    /*
     * For prompt input, we match the EOL without advance the input.
     * So the prompt will show after the current parse tree is processed.
     * When the current parse tree is processed, the next call to
     * parse() will advance the prompt input.
     */
    if (source.type == SOURCE_TYPE_FILE) {
        match_token(EOL);
    }
    else if (source.type == SOURCE_TYPE_PROMPT) {
        match_token_no_advance(EOL);
    }
    else { // SOURCE_TYPE_STRING
        if (tag == EOL)
            match_token(EOL);
        else
            match_token(ENDMARK);
    }
    return n;
}

Node *parse_simple_stmt(Node *p) {
    Node * n = addchild(p, SIMPLE_STMT, NULL, source.row);
    if (tag == PRINT) {
        parse_print_stmt(n);
    } else if (tag == READ) {
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
        t->type = R_EXPR;
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
        parse_funcdef(n);
    } else if (tag == CLASS) {
        parse_classdef(n);
    } else { // tag == TRY
        parse_try_stmt(n);
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

Node *parse_funcdef(Node *p) {
    Node *n = addchild(p, FUNCDEF, NULL, source.row);
    parse_token(n, DEF, NULL);
    parse_token(n, IDENT, lexeme);
    parse_token(n, '(', NULL);
    if (tag != ')') {
        parse_parmlist(n);
    }
    parse_token(n, ')', NULL);
    parse_suite(n);
    return n;
}

Node *parse_classdef(Node *p) {
    Node *n = addchild(p, CLASSDEF, NULL, source.row);
    parse_token(n, CLASS, NULL);
    parse_token(n, IDENT, lexeme);
    parse_token(n, '(', NULL);
    if (tag != ')') {
        parse_token(n, IDENT, lexeme);
    }
    parse_token(n, ')', NULL);
    parse_suite(n);
    return n;
}

Node *parse_try_stmt(Node *p) {
    Node *n = addchild(p, TRY_STMT, NULL, source.row);
    parse_token(n, TRY, NULL);
    parse_suite(n);
    parse_catch_stmt(n);
    while (tag == CATCH) {
        parse_catch_stmt(n);
    }
    if (tag == FINALLY)
        parse_finally_stmt(n);
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
        // Only match the EOL token here without adding it.
        // EOL is not saved as part of the parse tree.
        match_token(EOL);
        while (tag != '}') {
            parse_statement(n);
        }
        parse_token(n, '}', NULL);
    }
    return n;
}

Node *parse_parmlist(Node *p) {
    Node *n = addchild(p, PARMLIST, NULL, source.row);

    if (tag != '*' && tag != DSTAR) {
        parse_oparm_list(n);
        if (tag == ')')
            return n;
    }

    if (tag == '*') {
        parse_token(n, '*', NULL);
        parse_token(n, IDENT, lexeme);
        if (tag != ',')
            return n;
        else
            parse_token(n, ',', NULL);
    }

    parse_token(n, DSTAR, NULL);
    parse_token(n, IDENT, lexeme);
    return n;
}

Node *parse_oparm_list(Node *p) {
    Node *n = addchild(p, OPARM_LIST, NULL, source.row);
    parse_oparm(n);
    while (tag == ',') {
        parse_token(n, ',', NULL);
        if (tag == '*' || tag == DSTAR)
            return n;
        parse_oparm(n);
    }
    return n;
}

Node *parse_oparm(Node *p) {
    Node *n = addchild(p, OPARM, NULL, source.row);
    // parse_kvpair can return an identifier instead
    parse_kvpair(n);
    return n;
}

Node *parse_kvpair(Node *p) {
    Node *n = addchild(p, KVPAIR, NULL, source.row);
    parse_token(n, IDENT, lexeme);
    if (tag == '=') { // it is a kvpair
        parse_token(n, '=', NULL);
        parse_expr(n);
    } else { // it is just an expr
        n->type = IDENT;
        n->lexeme = CHILD(n,0)->lexeme;
        CHILD(n,0)->lexeme = NULL;
        free(CHILD(n,0));
        n->nchildren = 0;
        n->child = NULL;
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

Node *parse_catch_stmt(Node *p) {
    Node *n = addchild(p, CATCH_STMT, NULL, source.row);
    parse_token(n, CATCH, NULL);
    parse_token(n, '(', NULL);
    parse_token(n, IDENT, lexeme);
    parse_token(n, ',', NULL);
    parse_token(n, IDENT, lexeme);
    parse_token(n, ')', NULL);
    parse_suite(n);
    return n;
}

Node *parse_finally_stmt(Node *p) {
    Node *n = addchild(p, FINALLY_STMT, NULL, source.row);
    parse_token(n, FINALLY, NULL);
    parse_suite(n);
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
            if (tag != ')')
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
    Node *n = addchild(p, ARGLIST, NULL, source.row);
    parse_oarg(n);
    while (tag == ',') {
        parse_token(n, ',', NULL);
        parse_oarg(n);
    }
    return n;
}

Node *parse_oarg(Node *p) {
    Node *n = addchild(p, OARG, NULL, source.row);
    if (tag == IDENT) {
        parse_kvpair(n); // Can still return an expr
    } else {
        parse_expr(n);
    }
    return n;
}

void parse_idxrange_with_existing(Node *ex) {
    parse_token(ex, ':', NULL);
    if (tag != ':' && tag != ']')
        parse_expr(ex);

    if (tag == ':') {
        parse_token(ex, ':', NULL);
        if (tag != ':' && tag != ']')
            parse_expr(ex);
    }
}

void parse_idxlist_with_existing(Node *ex) {
    parse_token(ex, ',', NULL);
    parse_expr(ex);
    while (tag == ',') {
        parse_token(ex, ',', NULL);
        parse_expr(ex);
    }
}

Node *parse_subscription(Node *p) {
    Node *n = addchild(p, SUBSCRIPTION, NULL, source.row);
    Node *t;
    if (tag == ':') {
        parse_idxrange(n);
    } else {
        t = parse_singleidx(n);
        if (tag == ':') {
            t->type = IDXRANGE;
            parse_idxrange_with_existing(t);
        } else if (tag == ',') {
            t->type = IDXLIST;
            parse_idxlist_with_existing(n);
        }
    }
    return n;
}

Node *parse_singleidx(Node *p) {
    Node *n = addchild(p, SINGLEIDX, NULL, source.row);
    parse_expr(n);
    return n;
}

Node *parse_idxrange(Node *p) {
    Node *n = addchild(p, IDXRANGE, NULL, source.row);
    if (tag != ':')
        parse_expr(n);

    if (tag == ':') {
        parse_idxrange_with_existing(n);
    }
    return n;
}

static Node *
parse_token(Node *p, int token, char *lexeme) {
    // saved the lexeme since match_token changes it
    char *thisLexeme = (lexeme) ? strcpy(savedLexeme, lexeme) : lexeme;
    match_token(token);
    Node *n = addchild(p, token, thisLexeme, source.row);
    return n;
}

static Node *parse_magic_command(Node *p) {
    int mctag;
    if ((mctag = get_magic_action()) == MC_ERROR) {
        log_error(MAGIC_ERROR, "unknown magic command");
        longjmp(__parse_buf, 1);
    }
    addchild(p, mctag, NULL, source.row);
    if (mctag == MCA_RUN) {
        if ((mctag = get_magic_arg()) == MC_ERROR) {
            log_error(MAGIC_ERROR, "bad argument of magic command");
            longjmp(__parse_buf, 1);
        }
        addchild(p, mctag, lexeme, source.row);
    }
    tag = get_token();
    match_token_no_advance(EOL);
    p->type = MAGIC_COMMAND;
    return p;
}

