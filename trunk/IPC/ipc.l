%{
/*
 * IDL-Python-C (IPC) Mix programming language for fun.
 */

#include "ipc.h"
#include "ipc.tab.h"

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
"%" |             
"," |
";" |
"(" |            
")"                 { return yytext[0]; }



{INTEGER}           { yylval.dVal = atoi(yytext); return NUMBER; }
{FLOAT}             { yylval.dVal = atof(yytext); return NUMBER; }

print               { return PRINT; }
\"[^\"]*\"          { 
                        yylval.sVal = malloc(strlen(yytext)*sizeof(char));
                        strncpy(yylval.sVal, yytext+1, strlen(yytext)-2);
                        return STRING; }
{IDENTIFIER}        { 
                        yylval.sVal = malloc((strlen(yytext)+1)*sizeof(char));
                        strcpy(yylval.sVal, yytext); 
                        return ID; 
                    }
"\n"                { return EOL; }

"//".*              /* ignore comments */

{WHITESPACE}        /* ignore white space */

.                   { yyerror("Unrecognized character %c\n", *yytext); }

%%

