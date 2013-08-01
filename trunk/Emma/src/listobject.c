/*
 * listobject.c
 *
 *  Created on: 01/08/2013
 *      Author: ywangd
 */

#include "allobject.h"

EmObject *
newlistobject(unsigned int size) {
    EmListObject *lo;

    if (size == 0)
        size = DEFAULT_LIST_SIZE;

    if ((lo = NEWOBJ(EmListObject, &Listtype)) == NULL)
        return NULL;

    lo->size = size;
    lo->nitems = 0;

    if ((lo->list = (EmObject **) calloc(lo->size, sizeof(EmObject *)))
            == NULL) {
        DEL(lo);
        return log_error(MEMORY_ERROR, "not enough memory for list");
    }
    return (EmObject *)lo;
}

void listobject_free(EmObject *ob) {
    EmListObject *lo = (EmListObject *)ob;
    int i;
    for (i=0;i<lo->size;i++) {
        if (lo->list[i]) {
            DECREF(lo->list[i]);
        }
    }
    DEL(lo);
}



EmTypeObject Listtype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "list",                         // tp_name
        sizeof(EmListObject),           // tp_size
        0,                              // tp_itemsize

        listobject_free,                // tp_dealloc
        listobject_print,               // tp_print
        0,                              // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        0,                              // tp_hashfunc

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};
