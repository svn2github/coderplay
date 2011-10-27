#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symtab.h"

/* hash a string */
static unsigned
hashfunc (char *name)
{
    unsigned int hash = 0;
    unsigned c;
    while (c = *name++)
        hash = hash * 9 ^ c;
    return hash;
}

/* Search a string in the symbol table or create a new entry */
symbol_t *
lookup (char *name)
{
    symbol_t *sb = &symtab[hashfunc (name) % NMAX_SYMBOL];
    int scount = NMAX_SYMBOL;   /* how many have we looked at */

    while (--scount >= 0)
      {
          if (sb->name && !strcmp (sb->name, name))
            {
                return sb;
            }

          if (!sb->name)
            {                   /* new entry */
                sb->name = strdup (name);
                sb->refc = 0;
                sb->value = NULL;
                sb->st = NULL;
                sb->plist = NULL;
                return sb;
            }

          if (++sb >= symtab + NMAX_SYMBOL)
              sb = symtab;      /* try the next entry */
      }
    fprintf (stderr, "Internal error: symbol table overflow\n");
    exit (EXIT_FAILURE);        /* tried them all, table is full */
}

void 
delete_symbol(symbol_t *sym) 
{
    if (!sym->name) return;
    free(sym->name);

    if (sym->value) free(sym->value);
    if (sym->st) free(sym->st);
    if (sym->plist) free(sym->plist);
}

void delete_symtab()
{
    symbol_t * sb;
    int ii;

    for (ii=0;ii<NMAX_SYMBOL;ii++) {
        sb = symtab + ii;
        /* delete any pointer assciated with the symbol */
        delete_symbol(sb);
    }
}
