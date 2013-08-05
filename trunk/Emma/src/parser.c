#include "parser.h"
#include "parser.i"

int tag;

static int match_token(int t) {
    if (tag == t) {
        tag = get_token(); // get next token
        return 1;
    } else {
        log_error(SYNTAX_ERROR, "Unexpected token");
        return 0;
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

// Forward declaration
static Node * parse_token(Node *, int, char *);

Node *parse_file_input() {
    Node *ptree = newparsetree(FILE_INPUT);
    do {
        parse_statement(ptree);
    } while (tag != ENDMARK);
    return ptree;
}

Node *parse_prompt_input() {
    Node *ptree = newparsetree(PROMPT_INPUT);
    parse_statement(ptree);
    return ptree;
}

Node *parse_string_input() {
    Node *ptree = newparsetree(STRING_INPUT);
    do {
        parse_statement(ptree);
    } while (tag != ENDMARK);
    return ptree;
}

/*
 * At the end of each parse_xxx, the tag is set to first token
 * of next language struct.
 */
Node *parse_statement(Node *p) {
    Node * n;

    do {
        tag = get_token();
    } while (tag == EOL);
    n = addchild(p, STATEMENT, NULL, source.row);

    if (tag == IF || tag == WHILE || tag == FOR || tag == DEF
            || tag == CLASS || tag == TRY) {
        parse_compound_stmt(n);
    } else {
        parse_simple_stmt(n);
    }
    return n;
}

Node *parse_simple_stmt(Node *p) {
    Node * n = addchild(p, SIMPLE_STMT, NULL, source.row);
    if (tag == PRINT) {
        parse_print_stmt(n);
    } else {

    }
}

Node *parse_print_stmt(Node *p) {
    Node *n = addchild(p, PRINT_STMT, NULL, source.row);
    tag = get_token();
    if (tag == '>') {
        parse_token(n, tag, NULL);
        parse_primary(n);
    }
    parse_expr_list(n);
    return n;
}

Node *parse_compound_stmt(Node *p) {

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

Node *parse_expr(Node *p) {
    Node *n = addchild(p, EXPR, NULL, source.row);
    parse_r_expr(n);
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
        addchild(n, tag, lexeme, source.row);
    } else {
        parse_token(n, IDENT, lexeme);
    }
    return n;
}

Node *parse_trailer(Node *p) {
    Node *n = addchild(p, TRAILER, NULL, source.row);
    if (tag == '(') {
        parse_token(n, '(', NULL);
        parse_arglist(n);
        parse_token(n, ')', NULL);
    } else if (tag == '[') {
        parse_token(n, '[', NULL);
        parse_subscription(n);
        parse_token(n, ']', NULL);
    } else {
        parse_token(n, '.', NULL);
        parse_token(n, IDENT, lexeme);
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
    match_token(token);
    Node *n = addchild(p, token, lexeme, source.row);
    return n;
}

Node *
parse() {

    int tag, ii;

    // Prompt for interactive input
    if (source.type == SOURCE_TYPE_PROMPT)
        fprintf(stdout, "%s ", source.PS1);

    do {

        // Get the next token
        tag = get_token();

        //
        if (source.type == SOURCE_TYPE_PROMPT && tag == EOL) {
            if (source.nulcb == 0 && source.isContinue == 0) {
                fprintf(stdout, "%s ", source.PS1);
            } else {
                fprintf(stdout, "%s ", source.PS2);
                for (ii = 0; ii < source.nulcb; ii++) {
                    fprintf(stdout, "%s", "    ");
                }
            }
            continue;
        }

        /*
         if (tag == ENDMARK) {
         fprintf(stdout, "%5d  %-20s\n", tag, "END");
         } else if (tag == 10) {
         fprintf(stdout, "%5d  %-20s at line %d\n", tag, "EOL", source.row+1);
         } else if (tag < 256) {
         fprintf(stdout, "%5d  %-20c\n", tag, tag);
         } else if (tag == 256) {
         fprintf(stdout, "%5d  %-20s\n", tag, "**");
         } else if (tag == 257) {
         fprintf(stdout, "%5d  %-20s\n", tag, "<=");
         } else if (tag == 258) {
         fprintf(stdout, "%5d  %-20s\n", tag, "==");
         } else if (tag == 259) {
         fprintf(stdout, "%5d  %-20s\n", tag, ">=");
         } else if (tag == 260) {
         fprintf(stdout, "%5d  %-20s\n", tag, "!=");
         } else if (tag > 300) { // ID, numbers, strings
         fprintf(stdout, "%5d  %-20s\n", tag, lexeme);
         } else { // keywords
         fprintf(stdout, "%5d  %-20s\n", tag, lexeme, strlen(lexeme));
         }
         */

        /*
         * Handle the prompt for interactive input. Blank
         * lines do not counter for line numbers in interactive
         * input.
         */
        if (source.type == SOURCE_TYPE_PROMPT && tag == EOL) {
            if (source.nulcb == 0 && source.isContinue == 0) {
                fprintf(stdout, "%s ", source.PS1);
            } else {
                fprintf(stdout, "%s ", source.PS2);
                for (ii = 0; ii < source.nulcb; ii++) {
                    fprintf(stdout, "%s", "    ");
                }
            }
        }

        if (tag == EOL) {
            source.row++;
            source.isContinue = 0;
        }



        /*
         * Start parsing
         */

    } while (tag != ENDMARK);

    return NULL;
}

