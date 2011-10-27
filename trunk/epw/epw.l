%{
/*
 * IDL-Python-C (IPC) Mix programming language for fun.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symtab.h"
#include "syntree.h"
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

print               { return PRINT; }


({INTEGER}|{FLOAT}) {
                        yylval.d = malloc(sizeof(double)); 
                        *yylval.d = atof(yytext); 
                        return NUMBER; 
                    }

\"[^\"]*\"          { 
                        yylval.s = strdup(yytext+1);
                        yylval.s[yyleng-2] = 0;
                        return STRING; 
                    }

{IDENTIFIER}        { 
                        /* We either get the symbol from the symbol table or create a new entry */
                        yylval.sym = lookup(yytext);
                        return ID; 
                    }

({WHITESPACE}*";"{WHITESPACE}*)* { return ';'; }

({WHITESPACE}*";"{WHITESPACE}*)*"\n" { return EOL; }

"//".*              /* ignore comments */

{WHITESPACE}        /* ignore white space */

.                   { yyerror("Unrecognized character %c\n", *yytext); }

%%

