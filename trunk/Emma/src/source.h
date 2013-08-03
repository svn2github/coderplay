/*
 * source.h
 *
 *  Created on: 02/08/2013
 *      Author: ywangd
 */

#ifndef SOURCE_H_
#define SOURCE_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "token.h"

#define SOURCE_TYPE_FILE    0
#define SOURCE_TYPE_PROMPT  1
#define SOURCE_TYPE_STRING  2

typedef struct _source {
    int type;               // The input source type
    char *filename;         // The input file name
    FILE *fp;               // The input file handle
    char *line;             // The current input line
    char peek;              // The look ahead character
    char lastPeek;          // The last look ahead char
    int lastTag;            // The last returned tag
    int nulcb;              // number of unbalanced left curly bracket
    int isContinue;         // If set, the following reading are for line continuation
    unsigned int row;       // The current line number of the input line
    unsigned int pos;       // The current column number of the input line
    char PS1[10];           // prompt 1
    char PS2[10];           // prompt 2
} EmSource;

void nextc();
int matchc(char c);

extern EmSource source;

#endif /* SOURCE_H_ */
