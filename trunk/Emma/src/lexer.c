#include "lexer.h"
#include "lexer.i"

static Wordstable *wt;

char *line;
unsigned int len = 0;
unsigned int row = 0;
unsigned int pos = 0;
char peek = ' ';
Token *token;


void
lexer_init() {
    wt = wt_create(DEFAULT_WT_SIZE);
    WT_RESERVE_KEYWORDS();
    WT_RESERVE_COMPOSITE_OP();
    wt_dump(wt);

    line = (char *) malloc (BUFSIZ * sizeof(char));
    token = (Token *) malloc(sizeof(Token));
}

static void
nextc(FILE *fp) {
    if (pos >= 0 && pos < len) {
        peek = line[pos];
        pos++;
    }
    else {
        if (fgets(line, BUFSIZ-1, fp) == NULL) {
            peek = 0;
        } 
        else {
            peek = ' ';
            len = strlen(line);
            pos = 0;
        }
    }
}

static int
matchc(FILE *fp, char c) {
    nextc(fp);
    if (peek != c)
        return 0;
    peek = ' ';
    return 1;
}

Token *
get_token(FILE *fp, int lastTokenTag) {

    while (1) {
        // ignore whites and CR for linux 
        while (peek == ' ' || peek == '\t' || peek == CHAR_CR) nextc(fp);

        if (peek == 0) return NULL;

        if (peek == '#') {
            while (peek != CHAR_LF) nextc(fp);
        }

        if (peek == CHAR_LF) {
            while (peek == CHAR_LF) {
                row += 1;
                nextc(fp);
                // following line is to accomodate linux 
                if (peek == CHAR_CR) nextc(fp);
            }
            if (lastTokenTag != CHAR_LF) {
                token->tag = CHAR_LF;
                return token;
            }
            else {
                continue;
            }
        }

        if (peek == ';') {
            while (peek == ';') nextc(fp);
            if (lastTokenTag != ';' && lastTokenTag != CHAR_LF) {
                token->tag = ';';
                return token;
            }
            else {
                continue;
            }
        }


        if (peek == '>') {
            if matchc(fp, '=') {
                return wt_lookup(wt, ">=");
            }
            else {
                token->tag = '>';
                return token;
            }
        }
        else if (peek == '=') {
            if matchc(fp, '=') {
                return wt_lookup(wt, "==");
            }
            else {
                token->tag = '=';
                return token;
            }
        }
        else if (peek == '<') {
            if matchc(fp, '=') {
                return wt_lookup(wt, "<=");
            }
            else {
                token->tag = '<';
                return token;
            }
        }
        else if (peek == '*') {
            if matchc(fp, '*') {
                return wt_lookup(wt, "**");
            }
            else {
                token->tag = '*';
                return token;
            }
        }

        // Numbers
        //
        //
        // Strings
        //
        // Identifiers



        // Any single character token
        token->tag = peek;

        // Important, peek is set to blank so next call can proceed.
        peek = ' ';

        return token;
    }
}

void lexer_free() {
    wt_free(wt);
    free(line);
    free(token);
}

