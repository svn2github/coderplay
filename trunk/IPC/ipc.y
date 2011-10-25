%{

#include <stdio.h>
#include <stdarg.h>

extern FILE *yyin;

%}

%token PRINT STRING
%token INTEGER
%token ADD SUB MUL DIV ABS
%token EOL
%token OP CP /* open close paranthesis */

%%

statement_list
    : /* empty */
    | statement_list statement { printf("= %d\n> ", $2); }
    | statement_list EOL { printf("> "); }
    ; 

statement
    : int_math_exp EOL { $$ = $1; }
    | string EOL { $$ = $1; }
    ;

int_math_exp: factor
    | int_math_exp ADD factor { $$ = $1 + $3; }
    | int_math_exp SUB factor { $$ = $1 - $3; }
    ;

factor: term
    | factor MUL term { $$ = $1 * $3; }
    | factor DIV term { $$ = $1 / $3; }
    ;

term: INTEGER
    | ABS term { $$ = $2>=0?$2:-$2; }
    | OP int_math_exp CP { $$ = $2; }
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
print_error(char *format, ...) {
    va_list args;

    va_start(args, format);
    vfprintf(stdout, format, args);
    va_end(args);
    printf("\n");
}

yyerror(char* s)
{
    // fprintf(stderr, "error: %s\n", s);
    print_error(s);
}

