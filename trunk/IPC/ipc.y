%{

#include <stdio.h>
#include <stdarg.h>
#include "ipc.h"

extern FILE *yyin;

%}

%error-verbose

%union {
    char *sVal;
    double dVal;
    tnode_t *pnode;
}

/* Define operator precedence frow lowest to highest */
%left '+' '-' '%'
%left '*' '/'
/* %nonassoc '|'*/

%token PRINT
%token <sVal> ID
%token <dVal> NUMBER 
%token <sVal> STRING
%token EOL

%type <pnode> expr stmt

%%
program
    : /* empty */
    | program EOL { printf("[%d]> ", yylineno); }
    | program stmt EOL { printf(" = %f\n", eval($2)); PRINTLN; delete_node($2); }
    | program error EOL { yyerrok; printf("[%d]> ", yylineno); }
    ;

stmt
    : PRINT expr    { $$ = new_tnode(PRN, $2, NULL);}
    | expr
    ;

expr
    : NUMBER        { $$ = new_numnode($1); }
    | STRING        { $$ = new_strnode($1); }
    | expr '+' expr { $$ = new_tnode(ADD, $1, $3); }
    | expr '-' expr { $$ = new_tnode(SUB, $1, $3); }
    | expr '*' expr { $$ = new_tnode(MUL, $1, $3); }
    | expr '/' expr { $$ = new_tnode(DIV, $1, $3); }
    | expr '%' expr { $$ = new_tnode(MOD, $1, $3); }
    | '(' expr ')'  { $$ = $2; }
    | ID            { $$ = new_strnode($1); }
    ;


%%

int main(int argc, char **argv)
{
    if (argc > 1) {
        if (!(yyin = fopen(argv[1], "r"))) {
            perror(argv[1]);
        }
    } else {
        printf("IPC for fun\n");
        printf("[%d]> ", yylineno);
    }
    yyparse();

    //if (yylval.sVal) free(yylval.sVal);
    //if (yylval.pnode) free(yylval.pnode);
    return 0;
}

void 
yyerror(char *s, ...)
{
    va_list ap;
    va_start(ap, s);

    fprintf(stderr, "%d: error: ", yylineno);
    vfprintf(stderr, s, ap);
    fprintf(stderr, "\n");
}

