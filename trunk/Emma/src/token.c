#include "token.h"

Word *
new_word(char *lexeme, int tag) {
    Word *w = (Word *) malloc (sizeof(Word));
    w->lexeme = lexeme;
    w->tag = tag;
    return w;
}
