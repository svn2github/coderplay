#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "token.h"
#include "source.h"

extern char *lexeme;

void lexer_init();
int get_token();
void lexer_free();

