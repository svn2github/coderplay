%{
/*
 * IDL-Python-C (IPC) Mix programming language for fun.
 */

#include "ipc.tab.h"

int yylval;


%}

LETTER          [a-zA-Z_]
INTEGER         [0-9]+
IDENTIFIER      {LETTER}({LETTER}|{INTEGER})*
WHITESPACE      [\t ]+


%%

"+"                 { return ADD; }
"-"                 { return SUB; }
"*"                 { return MUL; }
"/"                 { return DIV; }
"|"                 { return ABS; }
{INTEGER}           { yylval = atoi(yytext); return INTEGER; }

\n                  { return EOL; }
print               { return PRINT; }
{IDENTIFIER}        { printf("IDENTIFIER: %s\n", yytext); }
\"[^"\n]*["\n]      { return STRING; }
"//".*              { printf("COMMENT\n"); } 
{WHITESPACE}        { }

.                   { printf("Unrecognized character %s\n", yytext); }

%%

