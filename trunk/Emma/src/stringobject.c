/*
 * stringobject.c
 *
 *  Created on: 29/07/2013
 *      Author: ywangd
 */
#include "allobject.h"

EmObject *
newstringobject(char *sval) {
    EmStringObject *ob;
    if ((ob = NEWOBJ(EmStringObject, &Stringtype)) == NULL)
        return NULL;
    ob->sval = (char *) malloc (sizeof(char)*(strlen(sval)+1));
    strcpy(ob->sval, sval);
    return (EmObject *)ob;
}

EmObject *
newstringobject_from_int(long ival) {
    sprintf(asString, "%l", ival);
    return newstringobject(asString);
}

EmObject *
newstringobject_from_float(double fval) {
    sprintf(asString, "%f", fval);
    return newstringobject(asString);
}

void stringobject_free(EmObject *ob) {
    DEL(((EmStringObject *)ob)->sval);
    DEL(ob);
}

void stringobject_print(EmObject *ob, FILE *fp) {
    fprintf(fp, "%s\n", ((EmStringObject *)ob)->sval);
}

EmObject *stringobject_tostr(EmObject *ob) {
    INCREF(ob);
    return ob;
}

long stringobject_hash(EmObject *ob) {
    unsigned char *p = (unsigned char *) (((EmStringObject *)ob)->sval);
    long hashval = *p << 7;
    while (*p != '\0')
        hashval = hashval + hashval + *p++;
    return hashval;
}


EmTypeObject Stringtype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "str",                          // tp_name
        sizeof(EmStringObject),         // tp_size
        0,                              // tp_itemsize

        stringobject_free,              // tp_dealloc
        stringobject_print,             // tp_print
        stringobject_tostr,             // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        stringobject_hash,              // tp_hashfunc

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};
