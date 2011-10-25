%{
/*
 * IDL-Python-C (IPC) Mix programming language for fun.
 */

#include "ipc.tab.h"
#include "ipc.h"

int yylval;


%}

%option noyywrap nodefault yylineno

LETTER          [a-zA-Z_]
INTEGER         -?[0-9]+
FLOAT           -?[0-9]*\.[0-9]*([eE][-+]?[0-9]+)?
IDENTIFIER      {LETTER}({LETTER}|{INTEGER})*
WHITESPACE      [\t ]+


%%

"+" |                
"-" |                
"*" |               
"/" |              
"|" |             
"(" |            
")"                 { return yytext[0]; }

{INTEGER}           { yylval = atoi(yytext); return INTEGER; }
{FLOAT}             { yylval = atof(yytext); printf("FLOAT\n"); }

print               { return PRINT; }
\"[^\"]*\"          { return STRING; }
\n                  { return EOL; }
"//".*              { printf("COMMENT\n"); } 
{IDENTIFIER}        { printf("IDENTIFIER: %s\n", yytext); }
{WHITESPACE}        { }

.                   { printf("Unrecognized character %c\n", *yytext); }

%%

