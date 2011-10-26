#define PRINTLN printf("[%d]> ", yylineno)

extern int yylineno; /* from lexer */
void yyerror(char *s, ...);

/* Define all types of nodes that can exist in the syntax tree */

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

tnode_t *new_tnode(int nodeType, tnode_t *l, tnode_t *r);
tnode_t *new_numnode(double val);
tnode_t *new_strnode(char* val);
void delete_node(tnode_t *pnode);

enum nodetype {
    NUMBER_CONSTANT = 258,
    STRING_LITERAL,
    ADD,
    SUB,
    MUL,
    DIV,
    MOD,
    PRN
};

double eval (tnode_t *pnode);

