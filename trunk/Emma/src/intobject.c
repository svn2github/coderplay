/*
 * intobject.c
 *
 *  Created on: 31/07/2013
 *      Author: ywangd
 */

#include "allobject.h"


EmObject *
newintobject(long ival) {
    EmIntObject *ob;
    if ((ob = NEWOBJ(EmIntObject, &Inttype)) == NULL)
        return NULL;
    ob->ival = ival;
    return (EmObject *)ob;
}

void intobject_free(EmObject *ob) {
    EmIntObject * iob = (EmIntObject *) ob;
    DEL(iob);
}

long getintvalue(EmObject *ob) {
    return ((EmIntObject *) ob)->ival;
}

void intobject_print(EmObject *ob, FILE *fp) {
    fprintf(fp, "%ld", ((EmIntObject *)ob)->ival);
}

char *intobject_tostr(EmObject *ob) {
    sprintf(asString, "%ld", ((EmIntObject *)ob)->ival);
    return asString;
}

int intobject_compare(EmObject *a, EmObject *b) {
    long u = ((EmIntObject *) a)->ival;
    long v = ((EmIntObject *) b)->ival;
    return (u < v) ? -1 : ((u > v) ? 1 : 0);
}

long intobject_hash(EmObject *ob) {
    long hashval = ((EmIntObject *)ob)->ival;
    if (hashval == -1)
        hashval = -2;
    return hashval;
}

int intobject_boolean(EmObject *ob) {
    return getintvalue(ob) != 0 ? 1 : 0;
}

static EmObject *
intobject_add(EmObject *u, EmObject *v) {
    if (v->type == &Inttype) {
        long x = getintvalue(u) + getintvalue(v);
        return newintobject(x);
    } else if (v->type == &Floattype) {
        double x = getintvalue(u) + getfloatvalue(v);
        return newfloatobject(x);
    } else {
        ex_type("operator + not supported by operands");
        return NULL;
    }
}

static EmObject *
intobject_sub(EmObject *u, EmObject *v) {
    if (v->type == &Inttype) {
        long x = getintvalue(u) - getintvalue(v);
        return newintobject(x);
    } else if (v->type == &Floattype) {
        double x = getintvalue(u) + getfloatvalue(v);
        return newfloatobject(x);
    } else {
        ex_type("operator - not supported by operands");
        return NULL;
    }
}

static EmObject *
intobject_neg(EmObject *ob) {
    return newintobject(-getintvalue(ob));
}

static EmNumberMethods int_as_number = {
        intobject_add,
        intobject_sub,
        0,
        0,
        0,
        0,
        intobject_neg,
};



EmTypeObject Inttype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "int",                          // tp_name
        sizeof(EmIntObject),            // tp_size
        0,                              // tp_itemsize

        intobject_free,                 // tp_dealloc
        intobject_print,                // tp_print
        intobject_tostr,                // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        intobject_compare,              // tp_compare
        intobject_hash,                 // tp_hashfunc
        intobject_boolean,              // tp_boolean

        &int_as_number,                 // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

