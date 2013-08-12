/*
 * compiler.h
 *
 *  Created on: 12/08/2013
 *      Author: ywangd
 */

#ifndef COMPILER_H_
#define COMPILER_H_

#include "Emma.h"

#define GET_OPCODE(c,n)       (c)->code[(n)++]
#define HAS_ARG(c)          (c > OP_HASARG ? 1: 0)

typedef struct _compiled {
    unsigned char *code;
    EmObject *consts;       // list of constants and compiled functions
    EmObject *names;        // list of variable names
    int nexti;              // index to code
    int len;               // length of code
} Compiled;


Compiled *compile_ast(AstNode *stree);


#endif /* COMPILER_H_ */
