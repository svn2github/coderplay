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
    return (EmObject *)ob;
}

void floatobject_free(EmObject *ob) {
    EmFloatObject * fob = (EmFloatObject *)ob;
    DEL(fob);
}

double getfloatvalue(EmObject *ob) {
    return ((EmFloatObject *) ob)->fval;
}

void floatobject_print(EmObject *ob, FILE *fp) {
    fprintf(fp, "%f", ((EmFloatObject *)ob)->fval);
}

EmObject *floatobject_tostr(EmObject *ob) {
    return newstringobject_from_float(getfloatvalue(ob));
}

int floatobject_compare(EmObject *a, EmObject *b) {
    double u = ((EmFloatObject *) a)->fval;
    double v = ((EmFloatObject *) b)->fval;
    return (u < v) ? -1 : ((u > v) ? 1 : 0);
}

int floatobject_boolean(EmObject *ob) {
    return ((EmFloatObject *)ob)->fval != 0.0 ? 1 : 0;
}

static EmObject *
floatobject_add(EmObject *u, EmObject *v) {
    double x;
    if (v->type == &Inttype) {
        x = getfloatvalue(u) + getintvalue(v);
        return newfloatobject(x);
    } else if (v->type == &Floattype) {
        x = getfloatvalue(u) + getfloatvalue(v);
        return newfloatobject(x);
    } else {
        ex_type("operator + not supported by operands");
        return NULL;
    }
}

static EmObject *
floatobject_sub(EmObject *u, EmObject *v) {
    double x;
    if (v->type == &Inttype) {
        x = getfloatvalue(u) - getintvalue(v);
        return newfloatobject(x);
    } else if (v->type == &Floattype) {
        x = getfloatvalue(u) - getfloatvalue(v);
        return newfloatobject(x);
    } else {
        ex_type("operator - not supported by operands");
        return NULL;
    }
}


static EmObject *
floatobject_neg(EmObject *ob) {
    return newfloatobject(-getfloatvalue(ob));
}


static EmNumberMethods float_as_number = {
        floatobject_add,
        floatobject_sub,
        0,
        0,
        0,
        0,
        floatobject_neg,
};


EmTypeObject Floattype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "float",                        // tp_name
        sizeof(EmFloatObject),          // tp_size
        0,                              // tp_itemsize

        floatobject_free,               // tp_dealloc
        floatobject_print,              // tp_print
        floatobject_tostr,              // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        floatobject_compare,            // tp_compare
        0,                              // tp_hashfunc
        floatobject_boolean,            // tp_boolean

        &float_as_number,               // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

