%{
/*
 * IDL-Python-C (IPC) Mix programming language for fun.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ipc.h"
#include "ipc.tab.h"

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
"," |
";" |
"(" |            
")"                 { return yytext[0]; }



({INTEGER}|{FLOAT})             { yylval.dVal = atof(yytext); return NUMBER; }

print               { return PRINT; }

\"[^\"]*\"          { 
                        yylval.sVal = strdup(yytext+1);
                        yylval.sVal[yyleng-2] = 0;
                        //yylval.sVal = malloc((strlen(yytext)+1)*sizeof(char));
                        //strncpy(yylval.sVal, yytext+1, sizeof(yytext+1)); 
                        return STRING; 
                    }

{IDENTIFIER}        { 
                        yylval.sVal = strdup(yytext);
                        //yylval.sVal = malloc((strlen(yytext)+1)*sizeof(char));
                        //strcpy(yylval.sVal, yytext); 
                        return ID; 
                    }

"\n"                { return EOL; }

"//".*              /* ignore comments */

{WHITESPACE}        /* ignore white space */

.                   { yyerror("Unrecognized character %c\n", *yytext); }

%%

