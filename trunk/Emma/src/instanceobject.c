/*
 * instanceobject.c
 *
 *  Created on: 26/08/2013
 *      Author: ywangd
 */

#include "allobject.h"

EmObject *
newinstanceobject(EmObject *class) {

    if (class->type != &Classtype) {
        ex_type("trying to create instance from non-class object");
        return NULL;
    }

    EmInstanceObject *ob;
    if ((ob = NEWOBJ(EmInstanceObject, &Instancetype)) == NULL)
        return NULL;

    INCREF(class);
    ob->class = class;

    if ((ob->attr = newhashobject()) == NULL) {
        ex_mem("no memory for instance's attr");
        DECREF(class);
        free(ob);
        return NULL;
    }

    return (EmObject *)ob;
}

void instanceobject_free(EmObject *ob) {
    EmInstanceObject *io = (EmInstanceObject *) ob;
    DECREF(io->class);
    DECREF(io->attr);
    free(io);
}

EmObject *getinstanceclass(EmObject *ob) {
    return ((EmInstanceObject *)ob)->class;
}

void instanceobject_print(EmObject *ob, FILE *fp) {
    fprintf(fp, "<instance object of class %x at 0x%08x>",
            (long)getinstanceclass(ob), (long)ob);
}

EmObject *instanceobject_getattr(EmObject *ob, char *name) {

    EmInstanceObject *io = (EmInstanceObject *) ob;
    EmObject *v, *x;

    // First try get the attribute from the instance's dict
    v = hashobject_lookup_by_string(io->attr, name);
    if (v != NULL) {
        return v;
    }

    // Second try get the attribute from the class and all the super class's dict
    v = classobject_getattr(getinstanceclass(ob), name);
    if (v == NULL) {
        return NULL;
    }

    // if it is a class function
    if (is_EmFuncObject(ob)) {
        // new instantiated class method
        x = newinstancemethodobject(ob, v);
        DECREF(v);
        return x;
    }

    // just an variable attribute
    return v;
}


EmTypeObject Instancetype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "instance",                          // tp_name
        sizeof(EmInstanceObject),            // tp_size
        0,                              // tp_itemsize

        instanceobject_free,                 // tp_dealloc
        instanceobject_print,                // tp_print
        0,                // tp_tostr
        instanceobject_getattr,         // tp_getattr
        0,                              // tp_setattr
        0,              // tp_compare
        0,                 // tp_hashfunc
        0,              // tp_boolean

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};



EmObject *newinstancemethodobject(EmObject *self, EmObject *func) {
    EmInstancemethodObject *ob;
    if ((ob = NEWOBJ(EmInstancemethodObject, &Instancemethodtype)) == NULL)
        return NULL;

    INCREF(self);
    ob->self = self;

    INCREF(func);
    ob->func = func;
}

void instancemethodobject_free(EmObject *ob) {
    EmInstancemethodObject *imo = (EmInstancemethodObject *) ob;
    DECREF(imo->self);
    DECREF(imo->func);
    free(imo);
}


EmTypeObject Instancemethodtype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "instance",                          // tp_name
        sizeof(EmInstancemethodObject),            // tp_size
        0,                              // tp_itemsize

        instancemethodobject_free,                 // tp_dealloc
        0,                // tp_print
        0,                // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,              // tp_compare
        0,                 // tp_hashfunc
        0,              // tp_boolean

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};
