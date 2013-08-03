#include "allobject.h"

char asString[AS_STRING_LENGTH];

/*
 * Following function can be used as placeholder for type object's
 * function pointers.
 */
void object_print(EmObject *ob, FILE *fp) {
    fprintf(fp, "<%s object at 0x%08x>\n", ob->type->tp_name, (unsigned int)ob);
}

char *object_tostr(EmObject *ob) {
    sprintf(asString, "<%s object at 0x%08x>", ob->type->tp_name, (unsigned int)ob);
    return asString;
}

/*
 * Convenience functions
 */

EmObject *newobj(EmTypeObject *tp) {
    EmObject *ob = (EmObject *) malloc(tp->tp_size);
    if (ob == NULL)
        return log_error(MEMORY_ERROR, "not enough memory");
    ob->type = tp;
    ob->nitems = 0;
    NEWREF(ob);
    return ob;
}

void freeobj(EmObject *ob) {
    if (ob->type->tp_dealloc)
        ob->type->tp_dealloc(ob);
}

void printobj(EmObject *ob, FILE *fp) {
    if (ob->type->tp_print == NULL) {
        object_print(ob, fp);
    } else {
        ob->type->tp_print(ob, fp);
    }
}

char *tostrobj(EmObject *ob) {
    if (ob->type->tp_tostr == NULL) {
        return object_tostr(ob);
    } else {
        return ob->type->tp_tostr(ob);
    }
}

EmObject *
getattr(EmObject *ob, char *name) {
    if (ob->type->tp_getattr == NULL) {
        log_error(TYPE_ERROR, "attribute-less object");
        return NULL;
    } else {
        return (*ob->type->tp_getattr)(ob, name);
    }
}

int setattr(EmObject *ob, char *name, EmObject *attr) {
    if (ob->type->tp_setattr == NULL) {
        if (ob->type->tp_getattr == NULL) {
            log_error(TYPE_ERROR, "attribute-less object");
        } else {
            log_error(TYPE_ERROR, "read-only attributes\n");
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
    return ((*tp->tp_compare)(ob1, ob2));
}

long hashobj(EmObject *ob) {
    if (ob->type->tp_hashfunc == NULL) {
        log_error(TYPE_ERROR, "unhashable type");
        return -1;
    }
    return (*ob->type->tp_hashfunc)(ob);
}


/*
 * The null object singleton
 */

void null_print(EmObject *ob, FILE *fp) {
    fprintf(fp, "null\n");
}

char *null_tostr(EmObject *ob) {
    return "null";
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

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

EmObject nulobj = {
        OB_HEAD_INIT(&Nulltype),
        0,
};

