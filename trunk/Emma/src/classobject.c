/*
 * classobject.c
 *
 *  Created on: 25/08/2013
 *      Author: ywangd
 */


#include "allobject.h"

EmObject *
newclassobject(EmObject *base, EmObject *attr) {
    EmClassObject *ob;
    if ((ob = NEWOBJ(EmClassObject, &Classtype)) == NULL)
        return NULL;

    if (base != NULL)
        INCREF(base);
    ob->base = base;
    INCREF(attr);
    ob->attr = attr;

    return (EmObject *)ob;
}

void classobject_free(EmObject *ob) {
    EmClassObject *clo = (EmClassObject *)ob;
    DECREF(clo->base);
    DECREF(clo->attr);
}

EmObject *
classobject_getattr(EmObject *ob, char *name) {
    EmClassObject *clo = (EmClassObject *)ob;
    EmObject *v;
    v = hashobject_lookup_by_string(clo->attr, name);
    if (v != NULL) {
        return v;
    }
    if (clo->base != NULL) {
        v = classobject_getattr(clo->base, name);
        if (v != NULL)
            return v;
    }
    ex_key_with_val("attribute not found", name);
    return NULL;
}


EmTypeObject Classtype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "class",                          // tp_name
        sizeof(EmClassObject),            // tp_size
        0,                              // tp_itemsize

        classobject_free,                 // tp_dealloc
        0,                // tp_print
        0,                // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,              // tp_compare
        0,                 // tp_hashfunc
        0,                              // tp_boolean

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};


