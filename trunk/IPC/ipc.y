%{

#include <stdio.h>

%}

%token PRINT STRING
%token INTEGER
%token ADD SUB MUL DIV ABS
%token EOL

%%

statement_list: 
    | statement_list exp EOL { printf("= %d\n>", $2); }
    | statement_list EOL { printf("> "); }
    | statement EOL { printf("print statement %s\n", $1); }
    | string EOL { printf("%s\n", $1); }
    ;

exp: factor
    | exp ADD factor { $$ = $1 + $3; }
    | exp SUB factor { $$ = $1 - $3; }
    ;

factor: term
    | factor MUL term { $$ = $1 * $3; }
    | factor DIV term { $$ = $1 / $3; }
    ;

term: INTEGER
    | ABS term { $$ = $2>=0?$2:-$2; }
    ;

statement: PRINT string { $$ = $2; }
    ;

string: STRING

%%

int main(int argc, char **argv)
{
    yyparse();
}

yyerror(char* s)
{
    fprintf(stderr, "error: %s\n", s);
}

