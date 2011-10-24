#include <stdio.h>
#include "parser.h"

extern FILE *yyin;

void
yyerror (char *msg)
{
  fprintf (stderr, "%s\n", msg);
}

int
main (int argc, char **argv)
{
  while (!feof (yyin))
    {
      yyparse ();
    }
}
