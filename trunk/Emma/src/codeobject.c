/*
 * codeobject.c
 *
 *  Created on: 15/08/2013
 *      Author: ywangd
 */


#include "allobject.h"




EmObject *
newcodeobject() {
    EmCodeObject *ob;
    if ((ob = NEWOBJ(EmCodeObject, &Codetype)) == NULL)
        return NULL;
    return (EmObject *)ob;
}

void codeobject_free(EmObject *ob) {

}

int codeobject_compare(EmObject *a, EmObject *b) {
    EmCodeObject *u;
    return 0;
}




EmTypeObject Codetype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "code",                         // tp_name
        sizeof(EmCodeObject),           // tp_size
        0,                              // tp_itemsize

        codeobject_free,                // tp_dealloc
        NULL,                           // tp_print
        NULL,                           // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        codeobject_compare,             // tp_compare
        NULL,                           // tp_hashfunc

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

