%{
/*
 * IDL-Python-C (IPC) Mix programming language for fun.
 */


%}

LETTER          [a-zA-Z_]
DIGIT           [0-9]
IDENTIFIER      {LETTER}({LETTER}|{DIGIT})*
WHITESPACE      [\t ]+


%%

\n                  { printf("End of line.\n"); }

print               { printf("Print\n"); }
{IDENTIFIER}        { printf("An identifier: %s\n", yytext); }
\"[^"\n]*["\n]      { printf("A string literal\n"); }
"//".*              { printf("A comment line\n"); } 
{WHITESPACE}        { printf("white spaces\n"); }

.                   ;

%%

