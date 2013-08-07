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
    source.lastPeek = source.peek;
    if (source.pos >= 0 && source.pos < strlen(source.line)) {
        source.peek = source.line[source.pos];
        source.pos++;
    } else {
        if (source.type == SOURCE_TYPE_FILE) {
            if (fgets(source.line, BUFSIZ - 1, source.fp) == NULL) {
                source.peek = ENDMARK;
            } else {
                source.peek = ' ';
                source.row++;
                source.pos = 0;
            }
        } else if (source.type == SOURCE_TYPE_PROMPT) {
            if (source.isContinue || source.nulcb > 0) {
                fprintf(stdout, "%s ", source.PS2);
            } else {
                fprintf(stdout, "%s ", source.PS1);
            }
            fgets(source.line, BUFSIZ - 1, source.fp);
            source.peek = ' ';
            source.row++;
            source.pos = 0;
        } else { // SOURCE_TYPE_STRING
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
        0,                      // nulcb
        0,                      // isContinue
        0,                      // row
        0,                      // column
        "In>",                  // PS1
        "...",                  // PS2
};


