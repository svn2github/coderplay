/**
  A words table for lexer implemented using a simple hashtable.
  */
#include "wordstable.h"
#include <assert.h>

static unsigned int prime_numbers[] = {
    3, 7, 13, 31, 61, 127, 251, 509, 1021, 2017, 4093,
    5987, 9551, 15683, 19609, 31397,
};

static unsigned int npnumbers = sizeof(prime_numbers) / sizeof(unsigned int);

unsigned int wt_getprime(unsigned int size) {
    int ii;
    for (ii=0; ii< npnumbers; ii++) {
        if (prime_numbers[ii] > size)
            return prime_numbers[ii];
    }
    fprintf(stderr, "Error: Wordstable size %d overflow.\n", size);
    return 0;
}

/*
 *  create the words table and initialise the parameters
 */
Wordstable *
wt_create(unsigned int size)
{
    unsigned int tsize;
    Wordstable * wtable;

    /* we want the size to be prime */
    if (!(tsize = wt_getprime(size))) {
        fprintf(stderr, "Error: Wordstable creation failed.\n");
        return NULL;
    }

    wtable = (Wordstable * ) malloc( sizeof(Wordstable ) );
    
    wtable->size = tsize; 
    wtable->nwords = 0;

    // table mem alloc and initialize to 0
    wtable->table = (WtEntry**) calloc( wtable->size, sizeof(WtEntry*) );

    return wtable;
}

/*
 *  free the words table 
 */
void
wt_free(Wordstable * wtable)
{
    int i;
    for(i=0;i<wtable->size;i++) {
        if( wtable->table[i] != NULL) {
            free(wtable->table[i]->lexeme);
            free(wtable->table[i]->word);
            free(wtable->table[i]);
        }
    }
    
    free( wtable->table );
    free( wtable );
}

/*
 *  this is the hash function
 */
unsigned long
wt_hash(char* lexeme)
{
    unsigned char *p = (unsigned char *) lexeme;
    unsigned long hashval = *p << 7;
    while (*p != '\0')
        hashval = hashval + hashval + *p++;
    return hashval; 
}
 
/*
 *  insert into hash table and rehash if loadfactor too high.
 */
Wordstable *
wt_install(Wordstable * wtable, char* lexeme, Word* word)
{
    unsigned long hashval;
    unsigned int idx, incr;
    WtEntry* new;

    /* rehash if too full */
    if( wtable->nwords*3 > wtable->size*2) {
        wtable = wt_rehash(wtable);
    }
    
    /* calculate the hash function */
    hashval = wt_hash(lexeme);
    idx = hashval % wtable->size;
    // calculate the increment for linear probing
    do {
        hashval = hashval + hashval + 1;
        incr = hashval % wtable->size;
    } while (incr ==0 );

    /* insert with linear probing */
    while( wtable->table[idx] != NULL && 
            strcmp(wtable->table[idx]->lexeme, lexeme)!=0 ) {
        idx = (idx+incr) % wtable->size;
    }

    if( wtable->table[idx] == NULL ) {
        /* insert the word */
        new = (WtEntry*) malloc(sizeof(WtEntry));
        new->lexeme = lexeme;
        new->word = word;
        wtable->table[idx] = new;
        wtable->nwords++;
    } else {
        fprintf(stderr,"Error: Trying install lexeme '%s' twice.\n", lexeme);
    }

    return wtable;
}

/*
 *  delete a lexeme + word pair from the hash table
 */
void
wt_delete(Wordstable * wtable,char* lexeme)
{
    unsigned long hashval;
    unsigned int idx, incr;
    
    /* calculate the hash function */
    hashval = wt_hash(lexeme);
    idx = hashval % wtable->size;
    // calculate the increment for linear probing
    do {
        hashval = hashval + hashval + 1;
        incr = hashval % wtable->size;
    } while (incr ==0 );

    while( wtable->table[idx] != NULL 
            && strcmp(wtable->table[idx]->lexeme,lexeme)!=0 ) {
        idx = (idx+incr) % wtable->size;
    }
    
    if( wtable->table[idx] == NULL ) {
        fprintf(stderr,"lexeme %s not found!\n",lexeme);
    } else {
        free(wtable->table[idx]->lexeme);
        free(wtable->table[idx]->word);
        free(wtable->table[idx]);
        wtable->table[idx] = NULL;
    }
}

/*
 *  check for membership of a lexeme
 */
Word *
wt_lookup(Wordstable * wtable,char* lexeme)
{
    unsigned long hashval;
    unsigned int idx, incr;
    
    /* calculate the hash function */
    hashval = wt_hash(lexeme);
    idx = hashval % wtable->size;
    // calculate the increment for linear probing
    do {
        hashval = hashval + hashval + 1;
        incr = hashval % wtable->size;
    } while (incr ==0 );
    
    while( wtable->table[idx] != NULL 
            && strcmp(wtable->table[idx]->lexeme,lexeme)!=0 ) {
        idx = (idx+incr) % wtable->size;
    }
    
    if( wtable->table[idx] == NULL ) {
        return NULL;
    } else {
        return wtable->table[idx]->word;
    }
}

/*
 *  resize the hash table so the load factor is ''normal'' again
 */
Wordstable *
wt_rehash(Wordstable * wtable)
{
    Wordstable * newtable;
    int size,i;
    
    /* calc new hash table size based on load factor */
    size = wt_getprime(wtable->nwords * 2);  // 50% load
    newtable = wt_create(size);
    
    /* rehash the values on the old hash table */
    for(i=0;i<wtable->size;i++) {
        if( wtable->table[i] != NULL) {
            wt_install(newtable, wtable->table[i]->lexeme,
                        wtable->table[i]->word );
        }
        free(wtable->table[i]);
    }
    
    // we cannot use wt_free since we don't wanna free the lexeme and word
    free(wtable->table);
    free(wtable);
    return newtable;
}

/*
 *  print for debug
 */
void
wt_dump(Wordstable * wtable)
{
    int i;
    
    /* output all lexeme + word pairs */
    fprintf(stdout,"%20s   %60s\n\n","lexeme","word");
    for(i=0;i<wtable->size;i++) {
        if( wtable->table[i] != NULL) {
            fprintf(stdout,"%20s   %120s\n",wtable->table[i]->lexeme,
                        wtable->table[i]->word->lexeme);
        }
    }
}


