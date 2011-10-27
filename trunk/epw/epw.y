%{

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include "symtab.h"
#include "syntree.h"
#include "epw.h"

extern FILE *yyin;

%}

%error-verbose

%union {
    char *s;
    double d;
    tnode_t *pnode;
    symbol_t *sym;
}

/* Define operator precedence frow lowest to highest */
%right '='
%left '+' '-' '%'
%left '*' '/'
/* %nonassoc '|'*/

%token PRINT
%token <sym> ID
%token <d> NUMBER 
%token <s> STRING
%token EOL

%type <pnode> line stmt_list stmt expr

%start program

%%
program
    : /* empty */ 
    | program line  { 
                        if ($2) {
                            printf("= %g\n", eval($2));
                            PRINTLN; 
                            delete_node($2);
                        } else {
                            printf("[%d]> ", yylineno); 
                        }
                    }
    | program error EOL { yyerrok; printf("[%d]> ", yylineno); }
    ;

line
    : EOL           { $$ = NULL; }
    | stmt_list EOL { $$ = $1; } 
    ;

stmt_list
    : stmt          { $$ = $1; }
    | stmt ';' stmt_list
                    { $$ = $1; }
    ;

stmt
    : PRINT expr    { $$ = new_tnode(PRN, $2, NULL);}
    | expr
    ;

expr
    : expr '+' expr { $$ = new_tnode(ADD, $1, $3); }
    | expr '-' expr { $$ = new_tnode(SUB, $1, $3); }
    | expr '*' expr { $$ = new_tnode(MUL, $1, $3); }
    | expr '/' expr { $$ = new_tnode(DIV, $1, $3); }
    | expr '%' expr { $$ = new_tnode(MOD, $1, $3); }
    | '(' expr ')'  { $$ = $2; }
    | NUMBER        { $$ = new_numnode($1); }
    | STRING        { $$ = new_strnode($1); }
    | ID            { $$ = new_symnode($1); }
    | ID '=' expr   { $$ = new_asnnode($1, $3); }
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

