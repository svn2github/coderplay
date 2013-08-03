#include "parser.h"

void *
parse() {

    lexer_init();

    int tag;

    int lastTag = CHAR_LF;

    if (source.type == SOURCE_TYPE_PROMPT)
        printf("%s ", source.PS1);

    do {

        lastTag = tag = get_token(lastTag);

        if (tag == ENDMARK) {
            printf("%5d  %-20s\n", tag, "END");
        } else if (tag == 10) {
            printf("%5d  %-20s at line %d\n", tag, "EOL", source.row);
            if (source.type == SOURCE_TYPE_PROMPT)
                printf("%s ", source.PS1);
        } else if (tag < 256) {
            printf("%5d  %-20c\n", tag, tag);
        } else if (tag == 256) {
            printf("%5d  %-20s\n", tag, "**");
        } else if (tag == 257) {
            printf("%5d  %-20s\n", tag, "<=");
        } else if (tag == 258) {
            printf("%5d  %-20s\n", tag, "==");
        } else if (tag == 259) {
            printf("%5d  %-20s\n", tag, ">=");
        } else if (tag == 260) {
            printf("%5d  %-20s\n", tag, "!=");
        } else if (tag > 300) { // ID, numbers, strings
            printf("%5d  %-20s\n", tag, lexeme);
        } else { // keywords
            printf("%5d  %-20s\n", tag, lexeme, strlen(lexeme));
        }

    } while (tag != ENDMARK);

    lexer_free();

    return NULL;
}

