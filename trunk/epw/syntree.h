/* Forward declaration of the struct */
#ifndef TREENODE_SYMBOL_STRUCT
#define TREENODE_SYMBOL_STRUCT
typedef struct tnode tnode_t;
typedef struct symlist symlist_t;
typedef struct symbol symbol_t;
#endif

/* Define all types of nodes that can exist in the syntax tree */
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

/* The standard tree node */
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

