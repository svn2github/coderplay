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
#include "allobject.h"
#include "source.h"
#include "lexer.h"
#include "parser.h"
#include "ast.h"

/*
 * Constant table (hashobject) that stores all constants
 * in the source file.
 */
extern EmObject *constTable;

#endif /* EMMA_H_ */
