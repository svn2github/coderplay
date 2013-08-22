/*
 * funcobject.c
 *
 *  Created on: 15/08/2013
 *      Author: ywangd
 */

#include "allobject.h"

EmObject *
newfuncobject(EmObject *co, struct _environment *env) {
    EmFuncObject *ob;
    if ((ob = NEWOBJ(EmFuncObject, &Functype)) == NULL)
        return NULL;
    ob->co = co;
    INCREF(co);
    ob->env = env;
    ob->extrap = NULL;
    ob->extrak = NULL;
    return (EmObject *)ob;
}

void funcobject_free(EmObject *ob) {
    EmFuncObject *fo = (EmFuncObject *)ob;
    if (fo->extrap)
        DECREF(fo->extrap);
    if (fo->extrak)
        DECREF(fo->extrak);

    DECREF(fo->co);
    DEL(fo);
}

void funcobject_print(EmObject *ob, FILE *fp) {
}

char *funcobject_tostr(EmObject *ob) {
    return NULL;
}


int funcobject_compare(EmObject *a, EmObject *b) {
    return 1;
}


EmTypeObject Functype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "func",                          // tp_name
        sizeof(EmFuncObject),            // tp_size
        0,                              // tp_itemsize

        funcobject_free,                 // tp_dealloc
        0,                // tp_print
        0,                // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,              // tp_compare
        0,                              // tp_hashfunc
        0,                              // tp_boolean

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

