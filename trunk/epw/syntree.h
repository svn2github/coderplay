/* Forward declaration of the struct */
#ifndef TREENODE_SYMBOL_STRUCT
#define TREENODE_SYMBOL_STRUCT
typedef struct tnode tnode_t;
typedef struct symlist symlist_t;
typedef struct symbol symbol_t;
#endif

/* Define all types of nodes that can exist in the syntax tree */
typedef enum
{
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
} nodetypeEnum;

/* The standard tree node */
struct tnode
{
    nodetypeEnum nodeType;
    /* 
     * The data can be a constant of numbers, string
     * or a symbol table entry. 
     */
    void *data;
    tnode_t *l;                 /* left operand */
    tnode_t *r;                 /* right operand */
};

tnode_t *new_tnode (int nodeType, void *data, tnode_t * l, tnode_t * r);

void delete_node (tnode_t * pnode);

