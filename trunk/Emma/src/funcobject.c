/*
 * funcobject.c
 *
 *  Created on: 15/08/2013
 *      Author: ywangd
 */

#include "allobject.h"

EmObject *
newfuncobject() {
    EmFuncObject *ob;
    if ((ob = NEWOBJ(EmFuncObject, &Functype)) == NULL)
        return NULL;
    return (EmObject *)ob;
}

void funcobject_free(EmObject *ob) {

}

void funcobject_print(EmObject *ob, FILE *fp) {
}

char *funcobject_tostr(EmObject *ob) {
    return NULL;
}


int funcobject_compare(EmObject *a, EmObject *b) {
    return 0;
}


EmTypeObject Functype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "int",                          // tp_name
        sizeof(EmFuncObject),            // tp_size
        0,                              // tp_itemsize

        funcobject_free,                 // tp_dealloc
        funcobject_print,                // tp_print
        funcobject_tostr,                // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        funcobject_compare,              // tp_compare
        0,                              // tp_hashfunc
        0,                              // tp_boolean

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

