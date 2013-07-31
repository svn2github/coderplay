#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "token.h"

#define DEFAULT_WT_SIZE 127
#define CHAR_CR         13
#define CHAR_LF         10

extern char *line;
extern unsigned int row;
extern unsigned int pos;
extern char *lexeme;

void lexer_init();
int get_token(FILE *fp, int lastTag);
void lexer_free();

