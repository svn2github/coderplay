#include "allobject.h"
#include "lexer.h"
#include "lexer.i"


char *line;
unsigned int len = 0;
unsigned int row = 0;
unsigned int pos = 0;
char *lexeme;

char peek = ' ';
char lastPeek = ' ';

void
lexer_init() {
    line = (char *) malloc (BUFSIZ * sizeof(char));
    lexeme = (char *) malloc (BUFSIZ * sizeof(char));
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

int
get_token(FILE *fp, int lastTokenTag) {

    int tag;
    int length;
    char quote;

    while (1) {
        // ignore whites and CR for linux 
        while (peek == ' ' || peek == '\t' || peek == CHAR_CR)
            nextc(fp);

        if (peek == 0)
            return ENDMARK; // end of INPUT

        if (peek == '#')
            while (peek != CHAR_LF)
                nextc(fp);

        if (peek == CHAR_LF) {
            while (peek == CHAR_LF) {
                row += 1;
                nextc(fp);
                // following line is to accomodate linux 
                if (peek == CHAR_CR) nextc(fp);
            }
            if (lastTokenTag != CHAR_LF)
                return CHAR_LF;
            else
                continue;

        }

        if (peek == ';') {
            while (peek == ';') nextc(fp);
            if (lastTokenTag != ';' && lastTokenTag != CHAR_LF)
                return ';';
            else
                continue;
        }

        if (peek == '>') {
            if (matchc(fp, '='))
                return GE;
            else
                return '>';
        }
        else if (peek == '=') {
            if (matchc(fp, '='))
                return EQ;
            else
                return '=';
        }
        else if (peek == '<') {
            if (matchc(fp, '='))
                return LE;
            else
                return '<';
        }
        else if (peek == '*') {
            if (matchc(fp, '*'))
                return DSTAR;
            else
                return '*';
        }

        // Numbers
        if (isdigit(peek)) {

        }

        // Strings
        length = 0;
        //printf("peek %c\n", peek);
        if (peek == '"' || peek == '\'') {
            quote = peek;
            do {
                lastPeek = peek;
                nextc(fp);
                lexeme[length++] = peek;
            } while (!(peek == quote && lastPeek != '\\'));
            lexeme[--length] = '\0'; // -- to erase ending quote
            nextc(fp); // read pass the ending quote
            return STRING;
        }

        length = 0;
        // Identifiers
        if (isalpha(peek) || peek == '_') {
            while (isalnum(peek) || peek == '_') {
                lexeme[length++] = peek;
                nextc(fp);
            }
            lexeme[length] = '\0';
            tag = match_keyword();
            if (tag) // keywords
                return tag;
            else // identifier
                return IDENT;
        }

        // Any single character token
        tag = peek;

        // Important, peek is set to blank so next call can proceed.
        peek = ' ';

        return tag;
    }
}

void lexer_free() {
    free(line);
    free(lexeme);
}

