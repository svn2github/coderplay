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
#include <string.h>
#include <ctype.h>
#include "allobject.h"
#include "node.h"
#include "source.h"
#include "lexer.h"
#include "parser.h"
#include "ast.h"
#include "opcode.h"
#include "compiler.h"
#include "vm.h"


/*
 * Constant table (hashobject) that stores all constants
 * in the source file.
 */
extern EmObject *literalTable;

#endif /* EMMA_H_ */
