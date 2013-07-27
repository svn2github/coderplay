#ifndef _TOKEN_H
#define _TOKEN_H

#include <stdio.h>
#include <stdlib.h>
#include "token.i"

typedef struct _token {
    int tag;
} Token;

typedef struct _word {
    int tag;
    char* lexeme;
} Word;

/*
 * The tokens are return by its lexeme instead of the converted
 * values of certain types. The conversion is defered to parse
 * tree or AST construction.
 */ 
typedef Word Integer;
typedef Word Float;
typedef Word String;

Word *new_word(char *lexeme, int tag);

#endif
