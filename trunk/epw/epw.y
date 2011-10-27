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
    double *d;
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
                            dataobj_t *dobj = eval($2);
                            if (dobj) {
                                printf("= ");
                                print_dataobj(dobj);
                                delete_dataobj(dobj);
                            }
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
    : PRINT expr    { $$ = new_tnode(PRN, NULL, $2, NULL);}
    | expr
    ;

expr
    : expr '+' expr { $$ = new_tnode(ADD, NULL, $1, $3); }
    | expr '-' expr { $$ = new_tnode(SUB, NULL, $1, $3); }
    | expr '*' expr { $$ = new_tnode(MUL, NULL, $1, $3); }
    | expr '/' expr { $$ = new_tnode(DIV, NULL, $1, $3); }
    | expr '%' expr { $$ = new_tnode(MOD, NULL, $1, $3); }
    | '(' expr ')'  { $$ = $2; }
    | NUMBER        { $$ = new_tnode(NUM, $1, NULL, NULL); }
    | STRING        { $$ = new_tnode(STR, $1, NULL, NULL); }
    | ID            { $$ = new_tnode(SYM, $1, NULL, NULL); }
    | ID '=' expr   { $$ = new_tnode(ASN, NULL, new_tnode(SYM, $1, NULL, NULL), $3); }
    ;

%%

int main(int argc, char **argv)
{
    if (argc > 1) {
        if (!(yyin = fopen(argv[1], "r"))) {
            perror(argv[1]);
        }
    } else {
        printf("Emma Peiran Wang says hi\n");
        printf("[%d]> ", yylineno);
    }
    yyparse();

    /* release the resources used by the symbol table */
    delete_symtab();

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

