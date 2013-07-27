#include "parser.h"

void *
parse(FILE *fp, char *filename) {

    lexer_init();

    char *line;
    void *token;

    int lastTokenTag = '\n';

    token = get_token(fp, line, lastTokenTag);



    lexer_free();

    return NULL;
}

