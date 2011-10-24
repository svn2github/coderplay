%{

#include <stdio.h>

%}

%token PRINT STRING

%%

program
    : statement_list
    ;

statement_list
    : statement_list statement
    |
    ;

statement
    : PRINT STRING          { printf("print statement\n"); }
    ;


%%


