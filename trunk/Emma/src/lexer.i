#define WT_RESERVE(lexeme,tag) wt_install(wt, new_word(lexeme, tag))

#define WT_RESERVE_KEYWORDS() WT_RESERVE("and", 269); \
    WT_RESERVE("elif", 259); \
    WT_RESERVE("catch", 276); \
    WT_RESERVE("null", 267); \
    WT_RESERVE("if", 258); \
    WT_RESERVE("raise", 275); \
    WT_RESERVE("for", 262); \
    WT_RESERVE("self", 278); \
    WT_RESERVE("finally", 277); \
    WT_RESERVE("print", 256); \
    WT_RESERVE("import", 272); \
    WT_RESERVE("return", 266); \
    WT_RESERVE("read", 257); \
    WT_RESERVE("else", 260); \
    WT_RESERVE("break", 264); \
    WT_RESERVE("not", 271); \
    WT_RESERVE("class", 268); \
    WT_RESERVE("package", 273); \
    WT_RESERVE("try", 274); \
    WT_RESERVE("while", 261); \
    WT_RESERVE("continue", 263); \
    WT_RESERVE("or", 270); \
    WT_RESERVE("def", 265)

