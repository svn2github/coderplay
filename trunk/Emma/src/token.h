#ifndef _TOKEN_H_
#define _TOKEN_H_

#define ENDMARK         0

#define EOL             10

#define CHAR_LF         10
#define CHAR_CR         13

#define DSTAR           256
#define LE              257
#define EQ              258
#define GE              259
#define NE              260
#define PRINT           261
#define READ            262
#define IF              263
#define ELIF            264
#define ELSE            265
#define WHILE           266
#define FOR             267
#define CONTINUE        268
#define BREAK           269
#define DEF             270
#define RETURN          271
#define NUL             272
#define CLASS           273
#define AND             274
#define OR              275
#define NOT             276
#define IMPORT          277
#define PACKAGE         278
#define TRY             279
#define RAISE           280
#define CATCH           281
#define FINALLY         282
#define SELF            283
#define INTEGER         284
#define FLOAT           285
#define STRING          286
#define IDENT           287

extern char *token_types[];

#endif
