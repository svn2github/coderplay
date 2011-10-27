#define PRINTLN printf("[%d]> ", yylineno)

extern int yylineno; /* from lexer */
void yyerror(char *s, ...);

/* Define all types of nodes that can exist in the syntax tree */

typedef struct symlist symlist_t;
typedef struct symbol symbol_t;

/* The standard tree node */
typedef struct tnode tnode_t;

struct tnode
{
    int nodeType;
    tnode_t *l; /* left operand */
    tnode_t *r; /* right operand */
};

/* The number constant node */
typedef struct
{
    int nodeType;
    double val;
} numnode_t;

/* The string constant node */
typedef struct
{
    int nodeType;
    char *val;
} strnode_t;

/* The symbol node */
typedef struct
{
    int nodeType;
    symbol_t *sym;
} symnode_t;

typedef struct
{
    int nodeType;
    symbol_t *l;
    tnode_t *r;
} asnnode_t;

tnode_t *new_tnode(int nodeType, tnode_t *l, tnode_t *r);
tnode_t *new_numnode(double val);
tnode_t *new_strnode(char* val);
tnode_t *new_symnode(symbol_t *sym);
tnode_t *new_asnnode(symbol_t *l, tnode_t *r);

void delete_node(tnode_t *pnode);

typedef enum {
    NUM = 258,
    STR,
    SYM,
    ASN,
    ADD,
    SUB,
    MUL,
    DIV,
    MOD,
    PRN
} treenodetype;

struct symlist {
    symbol_t *sym;
    symlist_t *next;
};

/* The symbl table */
struct symbol {
    char *name;
    double value;
    tnode_t *udf; /* the user defined function defintion */
    symlist_t *paralist; /* the list of dummy parameters */
};

#define NMAX_SYMBOL 9997
symbol_t symtab[NMAX_SYMBOL];

/* Look up a name in the hash table or create a new entry if no match is found */
symbol_t * lookup(char *);


double eval(tnode_t *pnode);

