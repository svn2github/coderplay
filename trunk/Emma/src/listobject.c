/*
 * listobject.c
 *
 *  Created on: 01/08/2013
 *      Author: ywangd
 */

#include "allobject.h"

EmObject *
newlistobject(unsigned int size) {
    EmListObject *lo;

    if (size == 0)
        size = DEFAULT_LIST_SIZE;

    if ((lo = NEWOBJ(EmListObject, &Listtype)) == NULL)
        return NULL;

    lo->size = size;
    lo->nitems = 0;

    if ((lo->list = (EmObject **) calloc(lo->size, sizeof(EmObject *)))
            == NULL) {
        DEL(lo);
        return log_error(MEMORY_ERROR, "not enough memory for list");
    }
    return (EmObject *)lo;
}

void listobject_free(EmObject *ob) {
    EmListObject *lo = (EmListObject *)ob;
    int i;
    for (i=0;i<lo->size;i++) {
        if (lo->list[i]) {
            DECREF(lo->list[i]);
        }
    }
    DEL(lo->list);
    DEL(lo);
}

void listobject_print(EmObject *ob, FILE *fp) {
    EmListObject *lo = (EmListObject *)ob;
    int i;
    for (i=0;i<lo->nitems;i++) {
        fprintf(fp, "%s, ", tostrobj(lo->list[i]));
    }
}


unsigned int listobject_len(EmObject *ob) {
    return ob->nitems;
}

EmObject *
listobject_concate(EmObject *ob1, EmObject *ob2) {
    EmListObject *newlo = (EmListObject *) newlistobject(
            ob1->nitems + ob2->nitems);
    int i;
    for (i=0;i<ob1->nitems;i++) {
        newlo->list[i] = listobject_get(ob1, i);
    }
    for (i=0;i<ob2->nitems;i++) {
        newlo->list[i+ob2->nitems] = listobject_get(ob2, i);
    }
    return (EmObject *)newlo;
}


EmObject *listobject_get(EmObject *ob, int idx) {
    EmListObject *lo = (EmListObject *)ob;
    if (idx < 0)
        idx += lo->nitems;
    if (idx >= lo->nitems) {
        return log_error(INDEX_ERROR, "index out of list boundary");
    }
    INCREF(lo->list[idx]);
    return lo->list[idx];
}

int listobject_set(EmObject *ob, int idx, EmObject *val) {
    EmListObject *lo = (EmListObject *)ob;
    if (idx < 0)
        idx += lo->nitems;
    if (idx >= lo->nitems) {
        log_error(INDEX_ERROR, "index out of list boundary");
        return 0;
    }
    DECREF(lo->list[idx]);
    INCREF(val);
    lo->list[idx] = val;
    return 1;
}

EmObject *listobject_slice(EmObject *ob, int start, int end, int step) {
    EmListObject *lo = (EmListObject *)ob;
    if (start < 0)
        start += lo->nitems;
    if (end < 0)
        end += lo->nitems;
    if (start >= lo->nitems || end >= lo->nitems)
        return log_error(INDEX_ERROR, "slice out of list boundary");

    int nitems = (int) (fabs((start - end)/step) + 1);
    EmListObject *newlo = (EmListObject *) newlistobject(nitems);
    int i = 0;
    if (start <= end) {
        for (; start <= end; start += step) {
            newlo->list[i] = listobject_get(ob, start);
            i++;
        }
    } else {
        for (; start >= end; i -= step) {
            newlo->list[i] = listobject_get(ob, start);
            i++;
        }
    }
    return (EmObject *)newlo;
}

EmListObject *listobject_resize(EmListObject *lo) {
    int newnitems = lo->nitems * 2u; // 50% load
    EmObject ** tmp;
    tmp = (EmObject **) realloc(lo->list, newnitems * sizeof(EmObject *));
    if (tmp == NULL) {
        log_error(MEMORY_ERROR, "no memory to resize list");
    } else {
        size_t newsize, oldsize;
        oldsize = lo->size * sizeof(EmObject *);
        newsize = newnitems * sizeof(EmObject *);
        // Make sure the newly allocated space are filled with zeros.
        memset((char *)tmp + oldsize, 0, newsize - oldsize);
        lo->list = tmp;
        lo->size = newnitems;
    }
    return lo;
}

EmObject *listobject_append(EmObject *ob, EmObject *val) {
    EmListObject *lo = (EmListObject *) ob;
    if (lo->nitems * 3 > lo->size * 2) {
        lo = listobject_resize(lo);
    }
    INCREF(val);
    lo->list[lo->nitems] = val;
    lo->nitems++;
    return (EmObject *)lo;
}

EmObject *listobject_insert(EmObject *ob, int idx, EmObject *val) {
    EmListObject *lo = (EmListObject *)ob;
    if (idx < 0)
        idx += lo->nitems;
    if (idx >= lo->nitems) {
        log_error(INDEX_ERROR, "index out of list boundary");
        return NULL;
    }
    if (lo->nitems * 3 > lo->size * 2) {
        lo = listobject_resize(lo);
    }
    INCREF(val);
    memmove(lo->list[idx+1], lo->list[idx],
            sizeof(EmObject *) * (lo->nitems - 1 - idx));
    lo->list[idx] = val;
    lo->nitems++;
    return (EmObject *)lo;
}

EmObject *listobject_delete(EmObject *ob, int idx) {
    EmListObject *lo = (EmListObject *) ob;
    if (idx < 0)
        idx += lo->nitems;
    if (idx >= lo->nitems) {
        log_error(INDEX_ERROR, "index out of list boundary");
        return NULL;
    }
    EmObject *val = lo->list[idx];
    if (idx < lo->nitems - 1) { // not last entry
        memmove(lo->list[idx], lo->list[idx + 1],
                sizeof(EmObject *) * (lo->nitems - 1 - idx));
    }
    lo->list[lo->nitems - 1] = NULL;
    lo->nitems--;
    return val;
}

EmObject *listobject_pop(EmObject *ob) {
    return listobject_delete(ob, ob->nitems);
}

EmObject *listobject_shift(EmObject *ob) {
    return listobject_delete(ob, 0);
}

int listobject_index(EmObject *ob, EmObject *val) {
    EmListObject *lo = (EmListObject *) ob;
    int ii;
    for (ii=0;ii<lo->nitems;ii++) {
        if (cmpobj(lo->list[ii], val) == 0)
            return ii;
    }
    return -1;
}

static EmSequenceMethods list_as_sequence = {
        listobject_len,             // length
        listobject_concate,         // concatenate
        listobject_get,             // get subscript
        listobject_slice,           // get slice
        listobject_set,             // set subscript
        0,                          // set slice
};

int listobject_boolean(EmObject *ob) {
    return ((EmListObject *)ob)->nitems > 0 ? 1 : 0;
}

EmTypeObject Listtype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "list",                         // tp_name
        sizeof(EmListObject),           // tp_size
        0,                              // tp_itemsize

        listobject_free,                // tp_dealloc
        listobject_print,               // tp_print
        0,                              // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        0,                              // tp_hashfunc
        listobject_boolean,             // tp_boolean

        0,                              // tp_as_number
        &list_as_sequence,              // tp_as_sequence
        0,                              // tp_as_mapping
};
