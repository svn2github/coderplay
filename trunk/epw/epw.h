#define PRINTLN printf("[%d]> ", yylineno)

extern int yylineno;            /* from lexer */
void yyerror (char *s, ...);

dataobj_t *eval (tnode_t * pnode);
dataobj_t *op_arithmetic(dataobj_t *d1, dataobj_t *d2, int operation);
