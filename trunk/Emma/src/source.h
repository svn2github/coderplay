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
    unsigned int row;       // The current line number of the input line
    unsigned int pos;       // The current column number of the input line
    void (* nextc) ();      // Get next character
    int (* matchc) (char c);// match the given character
} EmSource;

extern EmSource source;

#endif /* SOURCE_H_ */
