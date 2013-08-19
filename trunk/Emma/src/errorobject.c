/*
 * errorobject.c
 *
 *  Created on: 29/07/2013
 *      Author: ywang@gmail.com
 */
#include "allobject.h"
#include "source.h"


// The singleton error object
EmErrorObject errobj = {
        OB_HEAD_INIT(&Errortype),
        0,  // nitems
        NO_ERROR,   // errorNumber
        NULL,       // message
};

int has_error() {
    if (errobj.errorNumber == NO_ERROR)
        return 0;
    else
        return 1;
}

void reset_error() {
    errobj.errorNumber = NO_ERROR;
    errobj.message = NULL;
}

void *log_error(int errorNumber, char *message) {

    errobj.errorNumber = errorNumber;
    errobj.message = message;
    return NULL;
}

static char *error_types[] = {
        "NoError",
        "MemoryError",
        "SystemError",
        "TypeError",
        "KeyError",
        "IndexError",
        "SyntaxError",
        "MagicError",
        "RUNTIME_ERROR",
};

void printerror() {
    fprintf(stderr, "---> %s\n", source.line);
    fprintf(stderr, "     %*c\n", source.pos, '^');
    fprintf(stderr, "%s: %s near <row %d, col %d>\n",
            error_types[errobj.errorNumber],
            errobj.message,
            source.row, source.pos);
}

/*
 * Fatal error indicates internal program design/coding bugs in contrast
 * to user errors.
 */
void fatal(char *message) {
    fprintf(stderr, "Fatal error: %s near <row %d, col %d>\n", message,
            source.row, source.pos);
    exit(1);
}

EmTypeObject Errortype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "error",                        // tp_name
        sizeof(EmTypeObject),           // tp_size
        0,                              // tp_itemsize

        0,                              // tp_dealloc
        0,                              // tp_print
        0,                              // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        0,                              // tp_hashfunc
        0,                              // tp_boolean

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
        };
