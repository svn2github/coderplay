/*
 * floatobject.c
 *
 *  Created on: 31/07/2013
 *      Author: ywangd
 */

#include "allobject.h"

EmObject *
newfloatobject(double fval) {
    EmFloatObject *ob;
    if ((ob = NEWOBJ(EmFloatObject, &Floattype)) == NULL)
        return NULL;
    ob->fval = fval;
    return (EmFloatObject *)ob;
}

void floatobject_free(EmObject *ob) {
    DEL((EmFloatObject *)ob);
}

void floatobject_print(EmObject *ob, FILE *fp) {
    fprintf(fp, "%f\n", ((EmFloatObject *)ob)->fval);
}

EmStringObject *floatobject_tostr(EmObject *ob) {
    return newstringobject_from_float(((EmFloatObject *)ob)->fval);
}


EmTypeObject Floattype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "int",                          // tp_name
        sizeof(EmFloatObject),          // tp_size
        0,                              // tp_itemsize

        floatobject_free,               // tp_dealloc
        floatobject_print,              // tp_print
        floatobject_tostr,              // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        0,                              // tp_hashfunc

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

