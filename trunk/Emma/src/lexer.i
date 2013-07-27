#define WT_RESERVE(lexeme,tag) wt_install(wt, new_word(lexeme, tag))

#define WT_RESERVE_KEYWORDS() wt=WT_RESERVE("and",269); \
wt=WT_RESERVE("elif",259); \
wt=WT_RESERVE("catch",276); \
wt=WT_RESERVE("null",267); \
wt=WT_RESERVE("if",258); \
wt=WT_RESERVE("raise",275); \
wt=WT_RESERVE("for",262); \
wt=WT_RESERVE("self",278); \
wt=WT_RESERVE("finally",277); \
wt=WT_RESERVE("print",256); \
wt=WT_RESERVE("import",272); \
wt=WT_RESERVE("return",266); \
wt=WT_RESERVE("read",257); \
wt=WT_RESERVE("else",260); \
wt=WT_RESERVE("break",264); \
wt=WT_RESERVE("not",271); \
wt=WT_RESERVE("class",268); \
wt=WT_RESERVE("package",273); \
wt=WT_RESERVE("try",274); \
wt=WT_RESERVE("while",261); \
wt=WT_RESERVE("continue",263); \
wt=WT_RESERVE("or",270); \
wt=WT_RESERVE("def",265)
