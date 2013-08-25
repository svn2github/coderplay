/*
 * xxxobject.c
 *
 * This is the template file to create more objects.
 *
 *  Created on: 15/08/2013
 *      Author: ywangd
 */



typedef struct _xxxobject {
    OB_HEAD;
} EmXXXObject;

extern EmTypeObject XXXtype;

EmObject *newxxxobject();






#include "allobject.h"

EmObject *
newxxxobject() {
    EmXXXObject *ob;
    if ((ob = NEWOBJ(EmXXXObject, &XXXtype)) == NULL)
        return NULL;
    return (EmObject *)ob;
}

void xxxobject_free(EmObject *ob) {

}

void xxxobject_print(EmObject *ob, FILE *fp) {
}

EmObject *xxxobject_tostr(EmObject *ob) {
    return NULL;
}


int xxxobject_compare(EmObject *a, EmObject *b) {
    return 0;
}

long xxxobject_hash(EmObject *ob) {
    return 0;
}

EmTypeObject XXXtype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "xxx",                          // tp_name
        sizeof(EmXXXObject),            // tp_size
        0,                              // tp_itemsize

        xxxobject_free,                 // tp_dealloc
        xxxobject_print,                // tp_print
        xxxobject_tostr,                // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        xxxobject_compare,              // tp_compare
        xxxobject_hash,                 // tp_hashfunc
        xxxobject_boolean,              // tp_boolean

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

