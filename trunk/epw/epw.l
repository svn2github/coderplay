%{
/*
 * IDL-Python-C (IPC) Mix programming language for fun.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "readline/readline.h"
#include "readline/history.h"
#include "symtab.h"
#include "syntree.h"
#include "datatype.h"
#include "epw.h"
#include "parser.h"

/* Redefine the input to flex to use readline */
#define YY_INPUT(buf,result,max_size) result = get_input(buf, max_size);

static int get_input(char *buf, int size)
{
    char *line;
    char prompt[50];
    if (feof(yyin)) return YY_NULL;
    sprintf(prompt, "[%d]>", yylineno);
    line = readline(prompt);
    if (!line) return YY_NULL;

    if (strlen(line) > size - 2) {
        yyerror("input line too long");
        return YY_NULL;
    }

    add_history(line);
    strcpy(buf, line);
    strcat(buf, "\n");
    free(line);
    return strlen(buf);
}

%}

%option noyywrap nodefault yylineno

LETTER          [a-zA-Z_]
EXP ([Ee][-+]?[0-9]+) 
IDENTIFIER      {LETTER}({LETTER}|[0-9])*
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


[0-9]+"."[0-9]*{EXP}? |
"."?[0-9]+{EXP}?    {
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

