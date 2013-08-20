/*
 * exceptionobject.c
 *
 *  Created on: 21/08/2013
 *      Author: ywangd
 */



#include "allobject.h"

EmObject *
newexceptionobject(char *errtype, char *message) {
    EmExceptionObject *ob;
    if ((ob = NEWOBJ(EmExceptionObject, &Exceptiontype)) == NULL)
        return NULL;
    ob->errtype = newstringobject(errtype);
    ob->message = newstringobject(message);
    if (ob->errtype == NULL || ob->message == NULL) {
        exceptionobject_free((EmObject*) ob);
        return NULL;
    }
    ob->value = NULL;
    return (EmObject *) ob;
}

void exceptionobject_free(EmObject *ob) {
    if (ob == NULL)
        return;
    EmExceptionObject *eo = (EmExceptionObject *)ob;
    if (eo->errtype)
        DECREF(eo->errtype);
    if (eo->message)
                DECREF(eo->message);
    if (eo->value)
        DECREF(eo->value);
    free(eo);
}

void exceptionobject_print(EmObject *ob, FILE *fp) {
    EmExceptionObject *eo = (EmExceptionObject *)ob;
    fprintf(fp, "[%s] %s", getstringvalue(eo->errtype),
            getstringvalue(eo->message));
    if (eo->value)
        fprintf(fp, ": %s", getstringvalue(eo->value));
}

char *exceptionobject_tostr(EmObject *ob) {
    return NULL;
}

#define exceptionobject_get_type(ob)    (((EmExceptionObject *)(ob))->errtype)


int exceptionobject_compare(EmObject *a, EmObject *b) {
    return cmpobj(exceptionobject_get_type(a), exceptionobject_get_type(b));
}

long exceptionobject_hash(EmObject *ob) {
    return 0;
}

int exceptionobject_boolean(EmObject *ob) {
    return 1;
}


void exception_set(EmObject *ob, char *value) {
    EmExceptionObject *eo = (EmExceptionObject *)ob;
    if (eo->value)
        DECREF(eo->value);
    eo->value = newstringobject(value);
}



EmTypeObject Exceptiontype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "exception",                          // tp_name
        sizeof(EmExceptionObject),            // tp_size
        0,                              // tp_itemsize

        exceptionobject_free,                 // tp_dealloc
        exceptionobject_print,                // tp_print
        0,                              // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        exceptionobject_compare,              // tp_compare
        0,                              // tp_hashfunc
        exceptionobject_boolean,        // tp_boolean

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

