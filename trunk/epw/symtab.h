#define NMAX_SYMBOL 9997

/* Forward declaration of the struct */
#ifndef TREENODE_SYMBOL_STRUCT
#define TREENODE_SYMBOL_STRUCT
typedef struct tnode tnode_t;
typedef struct symlist symlist_t;
typedef struct symbol symbol_t;
#endif

typedef enum {
    SYM_NUM = 258,
    SYM_STR
} symtypeEnum;

/* The symbol */
/* A symbol can be either a variable name or a function name */
struct symbol
{
    char *name;
    symtypeEnum symType;
    unsigned int refc; /* the reference count */
    /* 
     * The symbol value is used for when the symbol is a simple
     * type such as number or strings. 
     */
    void *value;
    /* Symbol of function use the syntax tree pointer to locate its actual code */
    tnode_t *st;                /* the syntax tree for an user defined function */
    symlist_t *plist;        /* the list of dummy parameters */
};

/* The symbol list */
struct symlist
{
    symbol_t *sym;
    symlist_t *next;
};

/* The symbol table */
symbol_t symtab[NMAX_SYMBOL];

/* Look up a name in the symbol table or create a new entry if no match is found */
symbol_t *lookup (char *);

void reset_symbol(symbol_t *sym);
void delete_symbol(symbol_t *sym);
void delete_symtab();
