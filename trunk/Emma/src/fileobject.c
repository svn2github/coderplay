/*
 * fileobject.c
 *
 *  Created on: 17/08/2013
 *      Author: ywangd
 */


#include "allobject.h"

EmObject *
newfileobject(FILE *fp, char *name) {
    EmFileObject *ob;
    if ((ob = NEWOBJ(EmFileObject, &Filetype)) == NULL)
        return NULL;
    ob->fp = fp;
    ob->name = newstringobject(name);
    return (EmObject *)ob;
}

void fileobject_free(EmObject *ob) {
    EmFileObject *fo = (EmFileObject *) ob;
    if (fo->fp != stderr && fo->fp != stdout && fo->fp != stdin) {
        fclose(fo->fp);
    }
    freeobj(fo->name);
    DEL(fo);
}

void fileobject_print(EmObject *ob, FILE *fp) {
    fprintf(fp, "<file object: %s>",
            getstringvalue(((EmFileObject *) ob)->name));
}

EmObject *fileobject_tostr(EmObject *ob) {
    char s[200];
    sprintf(s, "<file object: %s>",
            getstringvalue(((EmFileObject *) ob)->name));
    return newstringobject(s);
}

int fileobject_boolean(EmObject *ob) {
    return 1;
}

FILE *getfp(EmObject *ob) {
    return ((EmFileObject *)ob)->fp;
}

EmTypeObject Filetype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "file",                          // tp_name
        sizeof(EmFileObject),            // tp_size
        0,                              // tp_itemsize

        fileobject_free,                 // tp_dealloc
        fileobject_print,                // tp_print
        fileobject_tostr,                // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        0,                              // tp_hashfunc
        fileobject_boolean,              // tp_boolean

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

