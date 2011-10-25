%{

#include <stdio.h>
#include <stdarg.h>
#include "ipc.h"

extern FILE *yyin;

%}

%error-verbose

/* Define operator precedence frow lowest to highest */
%left '+' '-'
%left '*' '/'
%nonassoc '|'

%token PRINT STRING
%token INTEGER
%token EOL

%%

statement_list
    : /* empty */
    | statement_list statement { printf("= %d\n> ", $2); }
    | statement_list EOL { printf("> "); } /* blank line or comment */
    ; 

statement
    : int_math_exp EOL { $$ = $1; }
    | string EOL { $$ = $1; }
    ;

int_math_exp: factor
    | int_math_exp '+' factor { $$ = $1 + $3; }
    | int_math_exp '-' factor { $$ = $1 - $3; }
    ;

factor: term
    | factor '*' term { $$ = $1 * $3; }
    | factor '/' term { $$ = $1 / $3; }
    ;

term: INTEGER
    | '|' term { $$ = $2>=0?$2:-$2; }
    | '(' int_math_exp ')' { $$ = $2; }
    ;

/*
statement:
    | PRINT string { printf("here\n"); $$ = $2; }
    ;
*/

string: STRING { printf("STRING\n"); $$ = $1; }
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
        printf("> ");
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

