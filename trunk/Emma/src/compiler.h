/*
 * compiler.h
 *
 *  Created on: 12/08/2013
 *      Author: ywangd
 */

#ifndef COMPILER_H_
#define COMPILER_H_

#include "Emma.h"


typedef struct _compiled {
    char *code;
    EmObject *consts;       // list of constants and compiled functions
    EmObject *names;        // list of variable names
    int nexti;              // index to code
} Compiled;




#endif /* COMPILER_H_ */
