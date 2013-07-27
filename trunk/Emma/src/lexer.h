#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "token.h"
#include "wordstable.h"

#define DEFAULT_WT_SIZE 127
#define CHAR_CR         13
#define CHAR_LF         10

extern char *line;
extern unsigned int row;
extern unsigned int pos;

void lexer_init();
Token *get_token(FILE *fp, int lastTokenTag);
void lexer_free();

