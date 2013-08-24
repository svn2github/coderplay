/*
 * moduleobject.c
 *
 *  Created on: 19/08/2013
 *      Author: ywang@gmail.com
 */


#include "allobject.h"

EmObject *
newmoduleobject(char *name) {
    EmModuleObject *ob;
    if ((ob = NEWOBJ(EmModuleObject, &Moduletype)) == NULL)
        return NULL;
    ob->name = newstringobject(name);
    if (ob->name == NULL || ob->hash == NULL) {
        DEL(ob);
        return NULL;
    }
    return (EmObject *)ob;
}

void moduleobject_free(EmObject *ob) {
    EmModuleObject *mo = (EmModuleObject *)ob;
    if (mo->name != NULL)
        DECREF(mo->name);
    if (mo->hash != NULL)
        DECREF(mo->hash);
    DEL(mo);
}

void moduleobject_print(EmObject *ob, FILE *fp) {
    fprintf(fp, "<module '%s'>\n",
            getstringvalue(((EmModuleObject *)ob)->name));
}


EmTypeObject Moduletype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "module",                          // tp_name
        sizeof(EmModuleObject),            // tp_size
        0,                              // tp_itemsize

        moduleobject_free,                 // tp_dealloc
        moduleobject_print,                // tp_print
        0,                              // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        0,                              // tp_hashfunc
        0,                              // tp_boolean

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

