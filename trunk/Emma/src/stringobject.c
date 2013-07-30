/*
 * stringobject.c
 *
 *  Created on: 29/07/2013
 *      Author: ywangd
 */
#include "allobject.h"

typedef struct _stringobject {
    OB_HEAD; // nitems included
    char *sval;
} EmStringObject;

EmStringObject *
newstringobject(char *sval) {
    EmStringObject *ob;
    if ((ob = NEWOBJ(EmStringObject, &Stringtype)) == NULL)
        return NULL;
    ob->sval = (char *) malloc (sizeof(char)*(strlen(sval)+1));
    strcpy(ob->sval, sval);
    return ob;
}

void stringobject_free(EmStringObject *ob) {
    DEL(ob->sval);
    DEL(ob);
}

void stringobject_print(EmStringObject *ob, FILE *fp) {
    fprintf(fp, "%s\n", ob->sval);
}

char *stringobject_tostr(EmStringObject *ob) {
    return ob->sval;
}

EmTypeObject Stringtype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "str",                          // tp_name
        sizeof(EmStringObject),         // tp_size
        0,                              // tp_itemsize

        0,                              // tp_dealloc
        stringobject_print,             // tp_print
        stringobject_tostr,             // tp_str
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        0,                              // tp_hashfunc

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};
