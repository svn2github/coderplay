#define PRINTLN printf("[%d]> ", yylineno)


extern int yylineno;            /* from lexer */
void yyerror (char *s, ...);

/* Define the data type that the code can be evaluated to */
typedef enum
{
    DT_NUM = 258,
    DT_STR,
    DT_SYM,
    DT_NUL
} datatypeEnum;

typedef struct {
    datatypeEnum dataType;
    void *data;
} dataobj_t;

dataobj_t *createDataObj(datatypeEnum type, void *data);

dataobj_t *eval (tnode_t * pnode);
void print_dataobj(dataobj_t * dobj);
