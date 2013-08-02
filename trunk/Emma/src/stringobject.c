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
    sprintf(asString, "%ld", ival);
    return newstringobject(asString);
}

EmObject *
newstringobject_from_float(double fval) {
    sprintf(asString, "%f", fval);
    return newstringobject(asString);
}

void stringobject_free(EmObject *ob) {
    EmStringObject * sob = (EmStringObject *)ob;
    DEL(sob->sval);
    DEL(sob);
}

void stringobject_print(EmObject *ob, FILE *fp) {
    fprintf(fp, "%s\n", ((EmStringObject *)ob)->sval);
}

char *stringobject_tostr(EmObject *ob) {
    return ((EmStringObject *)ob)->sval;
}

/*
 * The convenience function cmpobj ensures the objects are of the same
 * type when the following is called.
 */
int stringobject_compare(EmObject *a, EmObject *b) {
    EmStringObject *u, *v;
    int lu, lv, minlen, cmp;

    u = (EmStringObject *) a;
    v = (EmStringObject *) b;
    lu = strlen(u->sval);
    lv = strlen(v->sval);
    minlen = (lu < lv) ? lu : lv;

    cmp = memcmp(u->sval, v->sval, minlen);
    if (cmp || (!cmp && lu == lv))
        return cmp;
    else
        return (lu < lv) ? -1 : 1;
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
        stringobject_compare,           // tp_compare
        stringobject_hash,              // tp_hashfunc

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};
