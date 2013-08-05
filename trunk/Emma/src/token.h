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
#define XOR             276
#define NOT             277
#define IMPORT          278
#define PACKAGE         279
#define TRY             280
#define RAISE           281
#define CATCH           282
#define FINALLY         283
#define SELF            284
#define INTEGER         285
#define FLOAT           286
#define STRING          287
#define IDENT           288

extern char *token_types[];

#endif
