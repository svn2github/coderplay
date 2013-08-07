#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "token.h"
#include "source.h"


#define MC_ERROR     1
#define MCA_EXIT      2
#define MCA_RUN       3
#define MC_ARG        100

extern char *lexeme;

void lexer_init();
int get_token();
int get_magic_action();
int get_magic_arg();
void lexer_free();

