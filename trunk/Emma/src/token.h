#ifndef _TOKEN_H
#define _TOKEN_H

#include "token.i"

#define NEW_WORD() w = (Word *) malloc (sizeof(Word))

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
typedef _word Integer;
typedef _word Float;
typedef _word String;

#endif
