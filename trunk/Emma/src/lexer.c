#include "lexer.h"
#include "lexer.i"

static Wordstable *wt;

unsigned int len = 0;
unsigned int row = 0;
unsigned long pos = 0;
char peek = ' ';


void
lexer_init() {

    *wt = wt_create(DEFAULT_WT_SIZE);
    WT_RESERVE_KEYWORDS();
    wt_dump(wt);
}

static void
nextc() {
    if (pos >= 0 && pos < len) {
        peek = line[pos];
        pos++;
    }
    else {
        peek = ''; // As end of line
    }

}

Token *
get_token(FILE *fp, char *line, int lastTokenTag) {

    static Token *token = NULL;
    if (token == NULL) {
        token = malloc(sizeof(Token));
    }

    if (pos >= len) {
        if (fgets(line, BUFSIZ, fp) == NULL) {
            return NULL; // end of input reached
        }
        peek = ' ';
        len = strlen(line);
        pos = 0;
    }

    while (1) {
        while (peek == ' ' || peek == '\t') nextc();

        if (peek == '') {
            fprintf(stderr, "EOF reached\n");
            exit(1);
        }

        if (peek == '#') {
            while (peek != '\n') nextc();
        }

        if (peek == '\n') {
            while (peek == '\n') {
                row += 1;
            }
            if (lastTokenTag != '\n') {
                token->tag = '\n';
                return token;
            }
            else {
                continue;
            }
        }

        if (peek == ';') {
            while (peek == ';') nextc();
            if (lastTokenTag != ';' && lastTokenTag != '\n') {
                token->tag = ';';
                return token;
            }
            else {
                continue;
            }
        }

        printf("here\n");
        return NULL;

    }

}

void lexer_free() {
    wt_free(wt);
}

