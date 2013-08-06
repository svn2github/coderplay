#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "token.h"
#include "source.h"


#define MAGIC_NONE      0
#define MAGIC_ERROR     1
#define MAGIC_EXIT      2

extern char *lexeme;

void lexer_init();
int get_token();
int get_magic();
void lexer_free();

