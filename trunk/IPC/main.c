#include <stdio.h>
/*
#include "parser.h"

extern FILE *yyin;

void
yyerror (char *msg)
{
  fprintf (stderr, "%s\n", msg);
}
*/

extern enum INTEGER;
extern int yylval;

int
main (int argc, char **argv)
{
/*
  while (!feof (yyin))
    {
      yyparse ();
    }
*/
    int tok;

    while(tok = yylex()) {
        printf("%d", tok);
        if (tok == INTEGER) 
            printf(" = %d\n", yylval);
        else 
            printf("\n");
    }
}
