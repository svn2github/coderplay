/*
 * intobject.c
 *
 *  Created on: 31/07/2013
 *      Author: ywangd
 */

#include "allobject.h"

typedef struct _intobject {
    OB_HEAD;
    long ival;
} EmIntObject;

EmIntObject *
newintobject(long ival) {
    EmIntObject *ob;
    if ((ob = NEWOBJ(EmIntObject, &Inttype)) == NULL)
        return NULL;
    ob->ival = ival;
    return ob;
}

void intobject_free(EmIntObject *ob) {
    DEL(ob);
}

void intobject_print(EmIntObject *ob, FILE *fp) {
    fprintf(fp, "%l\n", ob->ival);
}

EmStringObject *intobject_tostr(EmIntObject *ob) {
    return newstringobject_from_int(ob->ival);
}


EmTypeObject Inttype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "int",                          // tp_name
        sizeof(EmIntObject),            // tp_size
        0,                              // tp_itemsize

        intobject_free,                 // tp_dealloc
        intobject_print,                // tp_print
        intobject_tostr,                // tp_str
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        0,                              // tp_hashfunc

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

