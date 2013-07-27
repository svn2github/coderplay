#include "parser.h"

void *
parse(FILE *fp, char *filename) {

    lexer_init();

    Token *token;

    int lastTokenTag = CHAR_LF;

    while ((token = get_token(fp, lastTokenTag)) != NULL) {
        lastTokenTag = token->tag;


        printf("%d\n", token->tag);
    }

    lexer_free();

    return NULL;
}

