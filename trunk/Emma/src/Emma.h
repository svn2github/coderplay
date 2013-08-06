/*
 * Emma.h
 *
 *  Created on: 31/07/2013
 *      Author: ywangd
 */

#ifndef EMMA_H_
#define EMMA_H_

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <setjmp.h>
#include "allobject.h"
#include "source.h"
#include "lexer.h"
#include "parser.h"

/*
 * Constant table (hashobject) that stores all constants
 * in the source file.
 */
extern EmObject *constTable;

extern jmp_buf __parse_buf;

#endif /* EMMA_H_ */
