%{
/*
 * IDL-Python-C (IPC) Mix programming language for fun.
 */

#include "ipc.tab.h"

int yylval;
int lineno = 1;


%}

%option noyywrap nodefault yylineno

LETTER          [a-zA-Z_]
INTEGER         -?[0-9]+
FLOAT           -?[0-9]+\.[0-9]*([eE][-+]?[0-9]+)?
IDENTIFIER      {LETTER}({LETTER}|{INTEGER})*
WHITESPACE      [\t ]+


%%

"+"                 { return ADD; }
"-"                 { return SUB; }
"*"                 { return MUL; }
"/"                 { return DIV; }
"|"                 { return ABS; }

{INTEGER}           { yylval = atoi(yytext); return INTEGER; }
{FLOAT}             { printf("FLOAT\n"); }

print               { return PRINT; }
\"[^\"]*\"          { return STRING; }
\n                  { lineno++; return EOL; }
"("                 { return OP; }
")"                 { return CP; }
"//".*              { printf("COMMENT\n"); } 
{IDENTIFIER}        { printf("IDENTIFIER: %s\n", yytext); }
{WHITESPACE}        { }

.                   { printf("Unrecognized character %s\n", yytext); }

%%

