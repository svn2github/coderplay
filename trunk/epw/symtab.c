#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symtab.h"

/* hash a string */
static unsigned
hash(char *name)
{
  unsigned int hash = 0;
  unsigned c;
  while(c = *name++) hash = hash*9 ^ c;
  return hash;
}

/* Search a string in the symbol table or create a new entry */
symbol_t *
lookup(char *name)
{
  symbol_t *sp = &symtab[hash(name)%NMAX_SYMBOL];
  int scount = NMAX_SYMBOL;       /* how many have we looked at */

  while(--scount >= 0) {
    if(sp->name && !strcmp(sp->name, name)) { return sp; }

    if(!sp->name) {     /* new entry */
      sp->name = strdup(name);
      sp->value = 0;
      sp->udf = NULL;
      sp->paralist = NULL;
      return sp;
    }

    if(++sp >= symtab+NMAX_SYMBOL) sp = symtab; /* try the next entry */
  }
  fprintf(stderr, "Internal error: symbol table overflow\n");
  exit(EXIT_FAILURE); /* tried them all, table is full */
}



