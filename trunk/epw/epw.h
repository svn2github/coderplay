#define PRINTLN printf("[%d]> ", yylineno)

extern int yylineno; /* from lexer */
void yyerror(char *s, ...);

double eval (tnode_t * pnode);
