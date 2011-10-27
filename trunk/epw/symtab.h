#define NMAX_SYMBOL 9997

/* Forward declaration of the struct */
#ifndef TREENODE_SYMBOL_STRUCT
#define TREENODE_SYMBOL_STRUCT
typedef struct tnode tnode_t;
typedef struct symlist symlist_t;
typedef struct symbol symbol_t;
#endif

/* The symbol */
struct symbol {
    char *name;
    double value;
    tnode_t *udf; /* the user defined function defintion */
    symlist_t *paralist; /* the list of dummy parameters */
};

/* The symbol list */
struct symlist {
    symbol_t *sym;
    symlist_t *next;
};

/* The symbol table */
symbol_t symtab[NMAX_SYMBOL];

/* Look up a name in the symbol table or create a new entry if no match is found */
symbol_t * lookup(char *);

