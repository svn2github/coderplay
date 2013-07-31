#include "parser.h"

void *
parse(FILE *fp, char *filename) {

    lexer_init();

    int tag;

    int lastTag = CHAR_LF;

    while ((lastTag = tag = get_token(fp, lastTag)) != 0) {

        if (tag < 256) {
            printf("%5d %20c\n", tag, tag);
        } else if (tag == 256) {
            printf("%5d %20s\n", tag, "**");
        } else if (tag == 257) {
            printf("%5d %20s\n", tag, "<=");
        } else if (tag == 258) {
            printf("%5d %20s\n", tag, "==");
        } else if (tag == 259) {
            printf("%5d %20s\n", tag, ">=");
        } else if (tag == 260) {
            printf("%5d %20s\n", tag, "!=");
        } else if (tag > 300) { // ID, numbers, strings
            printf("%5d  %20s\n", tag, lexeme);
        } else { // keywords
            printf("%5d  %20s\n", tag, lexeme);
        }

    }

    lexer_free();

    return NULL;
}

