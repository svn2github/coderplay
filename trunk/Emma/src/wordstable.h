#ifndef _WORDSTABLE_H
#define _WORDSTABLE_H

#include <stdio.h>
#include <stdlib.h>
#include "token.h"

// Note that lexeme points to the same string as word->lexeme
// Do not double free
typedef struct {
    char *lexeme;
    Word *word;
} WtEntry;

typedef struct {
    /* size of the words table */
    int size;        
    /* number of items in the words table */
    int nwords;       
    WtEntry** table;  /* table entries */
} Wordstable;

Wordstable* wt_create(unsigned int size);

void wt_free(Wordstable* htable);

unsigned long wt_hash(char* lexeme);

Wordstable* wt_install(Wordstable* htable, Word* word);

void wt_delete(Wordstable* htable, char* lexeme);

Word* wt_lookup(Wordstable* htable, char* lexeme);

Wordstable* wt_rehash(Wordstable* htable);

void wt_dump(Wordstable* htable);

#endif
