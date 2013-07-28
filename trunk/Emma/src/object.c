#include "allobject.h"

char asString[AS_STRING_LENGTH];

EmObject * object_new(EmTypeObject *tp) {

    EmObject *ob = (EmObject *) malloc(tp->tp_size);

    ob->type = tp;
    ob->refcnt = 1;
    ob->base = NULL;
    ob->nitems = 0;

    return ob;
}

void object_free(EmObject *ob) {
    free(ob);
}

void object_print(EmObject *ob, FILE *fp) {
    fprintf(fp, "<%s object at %x>\n", ob->type->tp_name, ob);
}

char *object_str(EmObject *ob) {
    sprintf(asString, "<%s object at %x>\n", ob->type->tp_name, ob);
    return asString;
}

/*
 * Note object_getattr, object_setattr, object_compare are all generic
 * functions that can be used for other type of objects. They all have
 * the abilities to dynamically call related functions defined in the
 * type object.
 */
EmObject *
object_getattr(EmObject *ob, char *name) {
    if (ob->type->tp_getattr == NULL) {
        fprintf(stderr, "attribute-less object\n");
        return NULL;
    } else {
        return (*ob->type->tp_getattr)(ob, name);
    }
}

int object_setattr(EmObject *ob, char *name, EmObject *attr) {
    if (ob->type->tp_setattr == NULL) {
        if (ob->type->tp_getattr == NULL) {
            fprintf(stderr, "attribute-less object\n");
        } else {
            fprintf(stderr, "read-only attributes\n");
        }
        return NULL;
    } else {
        return (*ob->type->tp_setattr)(ob, name, attr);
    }
}

int object_compare(EmObject *ob1, EmObject *ob2) {
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

long object_hashfunc(EmObject *ob) {
    if (ob->type->tp_hashfunc == NULL) {
        fprintf(stderr, "object not hashable\n");
        return 0;
    }
    return (*ob->type->tp_hashfunc)(ob);
}

char *
null_str(EmObject *ob) {
    sprintf(asString, "null");
    return asString;
}

EmTypeObject Nulltype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // base
        0,                              // nitems
        "null",                         // tp_name
        sizeof(EmTypeObject),           // tp_size
        0,                              // tp_itemsize

        0,                              // tp_alloc
        0,                              // tp_dealloc
        object_print,                   // tp_print
        object_str,                     // tp_str
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        0,                              // tp_hashfunc

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};


