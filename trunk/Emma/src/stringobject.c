/*
 * stringobject.c
 *
 *  Created on: 29/07/2013
 *      Author: ywangd
 */
#include "allobject.h"

EmObject *
newstringobject(char *sval) {
    char *tval;
    if ((tval = (char *) malloc(sizeof(char) * strlen(sval) + 1)) == NULL) {
        ex_mem("no memory for new string");
        return NULL;
    }
    strcpy(tval, sval);
    EmStringObject *ob;
    if ((ob = NEWOBJ(EmStringObject, &Stringtype)) == NULL) {
        free(tval);
        return NULL;
    }
    ob->sval = tval;
    return (EmObject *) ob;
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
    free(sob->sval);
    free(sob);
}


char *getstringvalue(EmObject *ob) {
    return ((EmStringObject *)ob)->sval;
}


void stringobject_print(EmObject *ob, FILE *fp) {
    fprintf(fp, "'%s'", ((EmStringObject *)ob)->sval);
}

EmObject *stringobject_tostr(EmObject *ob) {
    return NULL;
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

unsigned long stringobject_hash(EmObject *ob) {
    unsigned char *p = (unsigned char *) getstringvalue(ob);
    long hashval = *p << 7;
    while (*p != '\0')
        hashval = hashval + hashval + *p++;
    return hashval;
}

int stringobject_boolean(EmObject *ob) {
    return strlen(((EmStringObject *) ob)->sval) > 0 ? 1 : 0;
}

int stringobject_len(EmObject *ob) {
    return strlen(((EmStringObject *) ob)->sval);
}

EmObject *
stringobject_concate(EmObject *a, EmObject *b) {
    int i = stringobject_len(a);
    int j = stringobject_len(b);
    char *s = (char *) malloc(sizeof(char) * (i + j + 1));
    strcpy(s, ((EmStringObject *) a)->sval);
    strcat(s, ((EmStringObject *) b)->sval);
    EmObject *ob = newstringobject(s);
    free(s);
    return ob;
}


static EmSequenceMethods string_as_sequence = {
        stringobject_len,
        stringobject_concate,
        0,
        0,
        0,
        0,
};



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
        stringobject_boolean,           // tp_boolean

        0,                              // tp_as_number
        &string_as_sequence,            // tp_as_sequence
        0,                              // tp_as_mapping
};
