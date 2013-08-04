#include "Emma.h"

int tag;

static int match_token(int t) {
    if (tag == t) {
        tag = get_token();
        return 1;
    } else {
        log_error(SYNTAX_ERROR, "Unexpected token");
        return 0;
    }
}

Node *parse_file() {
    Node *stree = newsyntaxtree(FILE_INPUT);
    do {
        parse_statement();
    } while (tag != ENDMARK);
}

Node *parse_prompt() {
    return parse_statement();
}

Node *parse_string() {
    do {
        parse_statement();
    } while (tag != ENDMARK);
}

Node *parse_statement() {
    tag = get_token();
    while (tag == EOL) {
        tag = get_token();
    }
    if (tag == ENDMARK) {
        return NULL;
    } else {
        return parse_stmt_list();
    }
}

Node *parse_stmt_list() {
    tag = get_token();
    if (tag == IF) {
        parse_compound_stmt();
    } else {
        parse_simple_stmt();
    }
}


Node *parse_compound_stmt() {

}

Node *parse_simple_stmt() {

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
        if (source.type == SOURCE_TYPE_PROMPT && tag == EOL
                && source.lastTag == EOL) {
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
        if (source.type == SOURCE_TYPE_PROMPT && tag == EOL ) {
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



        source.lastTag = tag;

        /*
         * Start parsing
         */


    } while (tag != ENDMARK);

    return NULL;
}

