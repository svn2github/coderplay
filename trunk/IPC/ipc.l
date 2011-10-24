%{
/*
 * IDL-Python-C (IPC) Mix programming language for fun and maybe real practice.
 */

#include <string.h>
#include "y.tab.h"

%}

LETTER          [a-zA-Z_]
DIGIT           [0-9]
IDENTIFIER      {LETTER}({LETTER}|{DIGIT})*
WHITESPACE      [\t ]+


%%

\n                  {return 0; }

print               {return PRINT;}
\"[^"\n]*["\n]      {return STRING;}
"//".*              {} /* Skip comments */
{WHITESPACE}        {} /* Do nothing */

.                   ;

%%

