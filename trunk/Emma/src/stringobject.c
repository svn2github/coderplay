/*
 * stringobject.c
 *
 *  Created on: 29/07/2013
 *      Author: ywangd
 */
#include "allobject.h"

typedef struct _stringobject {
    OB_HEAD; // nitems included
    char *sval;
} EmStringObject;

EmStringObject *
stringobject_new(char *sval) {
    EmStringObject *ob = NEWOBJ(EmStringObject, &Stringtype);
    if (ob == NULL)
        return NULL;
    ob->sval = (char *) malloc (sizeof(char)*(strlen(sval)+1));
    strcpy(ob->sval, sval);
    return ob;
}


EmTypeObject Stringtype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "str",                          // tp_name
        sizeof(EmStringObject),         // tp_size
        sizeof(char),                   // tp_itemsize

        0,                              // tp_alloc
        0,                              // tp_dealloc
        0,                              // tp_print
        0,                              // tp_str
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        0,                              // tp_hashfunc

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};
