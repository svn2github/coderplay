%{
/*
 * IDL-Python-C (IPC) Mix programming language for fun.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "epw.h"
#include "parser.h"

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
"%" |             
"=" |
"," |
"(" |            
")"                 { return yytext[0]; }

({WHITESPACE}*";"{WHITESPACE}*)* { return ';'; }


({INTEGER}|{FLOAT})             { yylval.d = atof(yytext); return NUMBER; }

print               { return PRINT; }

\"[^\"]*\"          { 
                        yylval.s = strdup(yytext+1);
                        yylval.s[yyleng-2] = 0;
                        return STRING; 
                    }

{IDENTIFIER}        { 
                        yylval.sym = lookup(yytext);
                        return ID; 
                    }

({WHITESPACE}*";"{WHITESPACE}*)*"\n" { return EOL; }

"//".*              /* ignore comments */

{WHITESPACE}        /* ignore white space */

.                   { yyerror("Unrecognized character %c\n", *yytext); }

%%

