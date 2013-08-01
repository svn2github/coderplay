/*
 * errorobject.c
 *
 *  Created on: 29/07/2013
 *      Author: ywang@gmail.com
 */
#include "allobject.h"


// The singleton error object
EmErrorObject errobj = {
        OB_HEAD_INIT(&Errortype),
        0,  // nitems
        NO_ERROR,   // errorNumber
        NULL,       // message
};

void * log_error(int errorNumber, char *message) {
    errobj.errorNumber = errorNumber;
    errobj.message = message;
    return NULL;
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

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
        };
