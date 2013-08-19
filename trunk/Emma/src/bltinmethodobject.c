/*
 * bltinmethodobject.c
 *
 *  Created on: 19/08/2013
 *      Author: ywang@gmail.com
 */

#include "allobject.h"


EmObject *
newbltinmethodobject(char *name, bo_method method, EmObject *self) {
    EmBltinmethodObject *ob;
    if ((ob = NEWOBJ(EmBltinmethodObject, &Bltinmethodtype)) == NULL)
        return NULL;
    ob->name = newstringobject(name);
    ob->method = method;
    ob->self = self;
    return NULL;
}

void bltinmethodobject_free(EmObject *ob) {
    EmBltinmethodObject *blto;
    blto = (EmBltinmethodObject *)ob;
    DECREF(blto->name);
    DECREF(blto->self);
    DEL(blto);
}

void bltinmethodobject_print(EmObject *ob, FILE *fp) {
    EmBltinmethodObject *blto;
    blto = (EmBltinmethodObject *) ob;
    if (blto->self == NULL) {
        fprintf(fp, "<built-in function '%s'>\n",
                getstringvalue(blto->name));
    } else {
        fprintf(fp, "<built-in method '%s' of %s type>\n",
                getstringvalue(blto->name), blto->self->type->tp_name);
    }
}

EmTypeObject Bltinmethodtype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "bltinmethod",                          // tp_name
        sizeof(EmBltinmethodObject),            // tp_size
        0,                              // tp_itemsize

        bltinmethodobject_free,                 // tp_dealloc
        bltinmethodobject_print,                // tp_print
        0,                // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,              // tp_compare
        0,                 // tp_hashfunc
        0,                               // tp_boolean

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};
