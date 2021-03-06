#include "allobject.h"

char asString[AS_STRING_LENGTH];

/*
 * Following function can be used as placeholder for type object's
 * function pointers.
 */
void object_print(EmObject *ob, FILE *fp) {
    fprintf(fp, "<%s object at 0x%08x>\n", ob->type->tp_name, (long)ob);
}

EmObject *object_tostr(EmObject *ob) {
    char s[200];
    sprintf(s, "<%s object at 0x%08x>", ob->type->tp_name, (long)ob);
    return newstringobject(s);
}

/*
 * Convenience functions
 */

EmObject *newobj(EmTypeObject *tp) {
    EmObject *ob = (EmObject *) malloc(tp->tp_size);
    if (ob == NULL) {
        ex_mem_with_val("no memory for object type", tp->tp_name);
        return NULL;
    }
    ob->type = tp;
    ob->nitems = 0;
    NEWREF(ob);
    return ob;
}

void freeobj(EmObject *ob) {
    if (ob == NULL)
        return;
    (*ob->type->tp_dealloc)(ob);
}

void printobj(EmObject *ob, FILE *fp) {
    if (ob->type->tp_print == NULL) {
        object_print(ob, fp);
    } else {
        (*ob->type->tp_print)(ob, fp);
    }
}

EmObject *tostrobj(EmObject *ob) {
    if (ob->type->tp_tostr == NULL) {
        return object_tostr(ob);
    } else {
        return (*ob->type->tp_tostr)(ob);
    }
}

EmObject *
getattr(EmObject *ob, char *name) {
    if (ob->type->tp_getattr == NULL) {
        ex_type("attribute-less object");
        return NULL;
    } else {
        return (*ob->type->tp_getattr)(ob, name);
    }
}

int setattr(EmObject *ob, char *name, EmObject *attr) {
    if (ob->type->tp_setattr == NULL) {
        if (ob->type->tp_getattr == NULL) {
            ex_type("attribute-less object");
        } else {
            ex_type_with_val("read-only attributes", name);
        }
        return 0;
    } else {
        return (*ob->type->tp_setattr)(ob, name, attr);
    }
}

int cmpobj(EmObject *ob1, EmObject *ob2) {
    EmTypeObject *tp;

    // Same object
    if (ob1 == ob2)
        return 0;
    // Un-allocated object is always smaller
    if (ob1 == NULL)
        return -1;
    if (ob2 == NULL)
        return 1;
    /*
     * If objects are different types, there really is no way to compare them.
     * So we just compare its name.
     */
    if ((tp = ob1->type) != ob2->type)
        return strcmp(tp->tp_name, ob2->type->tp_name);

    /*
     * If objects are of the same type but compare function is undefined.
     * We just compare their physical memory address
     */
    if (tp->tp_compare == NULL)
        return (ob1 < ob2) ? -1 : 1;

    // Normal comparison using the compare function defined for the object type.
    return (*tp->tp_compare)(ob1, ob2);
}

unsigned long hashobj(EmObject *ob) {
    if (ob->type->tp_hashfunc == NULL) {
        ex_type_with_val("unhashable type", ob->type->tp_name);
        return -1;
    }
    return (*ob->type->tp_hashfunc)(ob);
}

int boolobj(EmObject *ob) {
    if (ob->type->tp_boolean == NULL) {
        return 1;
    }
    return (*ob->type->tp_boolean)(ob);
}

/*
 * The null object singleton
 */

void null_print(EmObject *ob, FILE *fp) {
    fprintf(fp, "null");
}

EmObject *null_tostr(EmObject *ob) {
    return newstringobject("null");
}

int null_boolean(EmObject *ob) {
    return 0;
}

EmTypeObject Nulltype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "null",                         // tp_name
        sizeof(EmObject),               // tp_size
        0,                              // tp_itemsize

        0,                              // tp_dealloc
        null_print,                     // tp_print
        null_tostr,                     // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        0,                              // tp_hashfunc
        null_boolean,                   // tp_boolean

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

EmObject nulobj = {
        OB_HEAD_INIT(&Nulltype),
        0,
};

