/*
 * floatobject.c
 *
 *  Created on: 31/07/2013
 *      Author: ywangd
 */

#include "allobject.h"

EmFloatObject *
newfloatobject(double fval) {
    EmFloatObject *ob;
    if ((ob = NEWOBJ(EmFloatObject, &Floattype)) == NULL)
        return NULL;
    ob->fval = fval;
    return ob;
}

void floatobject_free(EmFloatObject *ob) {
    DEL(ob);
}

void floatobject_print(EmFloatObject *ob, FILE *fp) {
    fprintf(fp, "%f\n", ob->fval);
}

EmStringObject *floatobject_tostr(EmFloatObject *ob) {
    return newstringobject_from_float(ob->fval);
}


EmTypeObject Floattype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "int",                          // tp_name
        sizeof(EmFloatObject),          // tp_size
        0,                              // tp_itemsize

        floatobject_free,               // tp_dealloc
        floatobject_print,              // tp_print
        floatobject_tostr,              // tp_str
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        0,                              // tp_hashfunc

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

