/*
 * source.c
 * Manage different type of source input, including file, prompt and string.
 *
 *
 *  Created on: 02/08/2013
 *      Author: ywangd
 */
#include "source.h"

void nextc() {
    if (source.pos >= 0 && source.pos < strlen(source.line)) {
        source.peek = source.line[source.pos];
        source.pos++;
    } else {
        if (source.type == SOURCE_TYPE_FILE || source.type == SOURCE_TYPE_PROMPT) {
            if (fgets(source.line, BUFSIZ - 1, source.fp) == NULL) {
                source.peek = ENDMARK;
            } else {
                source.row += 1;
                source.peek = ' ';
                source.pos = 0;
            }
        } else {
            source.peek = ENDMARK;
        }
    }
}

int matchc(char c) {
    nextc();
    if (source.peek != c)
        return 0;
    source.peek = ' ';
    return 1;
}

EmSource source = {
        SOURCE_TYPE_FILE,       // type
        NULL,                   // filename
        NULL,                   // file handle
        NULL,                   // current line
        ' ',                    // peek
        ' ',                    // lastPeek
        0,                      // row
        0,                      // column
        "In>",
        "...",

};


