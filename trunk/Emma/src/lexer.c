#include "lexer.h"
#include "lexer.i"



Token *
lexer() {

    Wordstable *wt = wt_create(DEFAULT_WT_SIZE);
    WT_RESERVE_KEYWORDS();
    wt_dump(wt);

    wt_free(wt);

    return NULL;
}

