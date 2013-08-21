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
        ex_nomem("not enough memory for list");
        return NULL;
    }
    return (EmObject *)lo;
}

EmObject *
newlistobject_of_null(unsigned int size) {
    EmObject *ob = newlistobject(size);
    ob->nitems = size;
    int ii;
    for (ii=0;ii<size;ii++)
        listobject_set(ob, ii, &nulobj);
    return ob;
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
    fprintf(fp, "[");
    for (i=0;i<lo->nitems;i++) {
        printobj(lo->list[i], fp);
        if (i < lo->nitems - 1)
            fprintf(fp, ", ");
    }
    fprintf(fp, "]");
}

char *listobject_tostr(EmObject *ob) {
    EmListObject *lo = (EmListObject *)ob;
    int ii;
    for (ii=0;ii<lo->nitems;ii++) {

    }
    return NULL;
}


int listobject_len(EmObject *ob) {
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
    if (!is_EmListObject(ob)) {
        ex_badtype("wrong type for list set");
        return NULL;
    }
    EmListObject *lo = (EmListObject *)ob;
    if (idx < 0)
        idx += lo->nitems;

    if (idx >= lo->nitems) {
        ex_index("index out of list boundary");
        return NULL;
    }
    INCREF(lo->list[idx]);
    return lo->list[idx];
}

int listobject_set(EmObject *ob, int idx, EmObject *val) {
    if (!is_EmListObject(ob)) {
        ex_badtype("wrong type for list set");
        return 0;
    }
    EmListObject *lo = (EmListObject *)ob;
    if (idx < 0)
        idx += lo->nitems;

    if (idx >= lo->nitems) {
        ex_index("index out of list boundary");
        return 0;
    }
    if (lo->list[idx]) // check for NULL
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

    if (start >= lo->nitems || end >= lo->nitems) {
        ex_index("slice out of list boundary");
        return NULL;
    }

    int nitems = (int) (fabs((start - end)/step) + 1);
    EmListObject *newlo = (EmListObject *) newlistobject(nitems);
    newlo->nitems = nitems;
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

EmObject *listobject_slice_by_list(EmObject *ob, EmObject *slice) {
    EmObject *start, *end, *step;
    start = listobject_get(slice, 0);
    end = listobject_get(slice, 1);
    step = listobject_get(slice, 2);
    EmObject *newlo = listobject_slice(ob, getintvalue(start), getintvalue(end), getintvalue(step));
    DECREF(start);
    DECREF(end);
    DECREF(step);
    return newlo;
}

int listobject_set_slice(EmObject *ob, EmObject *slice, EmObject *val) {
    EmObject *startob, *endob, *stepob;
    startob = listobject_get(slice, 0);
    endob = listobject_get(slice, 1);
    stepob = listobject_get(slice, 2);

    int start, end, step;

    start = getintvalue(startob);
    end = getintvalue(endob);
    step = getintvalue(stepob);

    DECREF(startob);
    DECREF(endob);
    DECREF(stepob);

    int retval = 1;

    int nitems_0, nitems;
    nitems_0 = listobject_len(ob);
    if (start < 0)
        start += nitems_0;
    if (end < 0)
        end += nitems_0;

    if (start >= nitems_0 || end >= nitems_0) {
        ex_index("slice out of list boundary");
        retval = 0;
        goto end_listobject_set_slice;
    }

    nitems = (int) (fabs((start - end)/step) + 1);

    if (nitems != listobject_len(val)) {
        ex_runtime("number of items do not match for assignment");
        retval = 0;
        goto end_listobject_set_slice;
    }

    EmObject *item;
    int i = 0;
    if (start <= end) {
        for (; start <= end; start += step) {
            item = listobject_get(val, i);
            listobject_set(ob, start, item);
            DECREF(item);
            i++;
        }
    } else {
        for (; start >= end; i -= step) {
            item = listobject_get(val, i);
            listobject_set(ob, start, item);
            DECREF(item);
            i++;
        }
    }

    end_listobject_set_slice:

    return retval;
}

EmObject *listobject_idxlist(EmObject *ob, EmObject *idxlist) {
    EmListObject *newlo;
    EmObject *idx;
    int ii, nitems;
    nitems = listobject_len(idxlist);
    newlo = (EmListObject *)newlistobject(nitems);
    newlo->nitems = nitems;
    for (ii=0; ii<nitems; ii++) {
        idx = listobject_get(idxlist, ii);
        newlo->list[ii] = listobject_get(ob, getintvalue(idx));
        DECREF(idx);
    }
    return (EmObject *)newlo;
}

int listobject_set_idxlist(EmObject *ob, EmObject *idxlist, EmObject *val) {
    if (listobject_len(idxlist) != listobject_len(val)) {
        ex_runtime("number of items do not match for assignment");
        return 0;
    }
    int ii;
    EmObject *idx, *item;
    for (ii=0;ii<listobject_len(idxlist);ii++) {
        idx = listobject_get(idxlist, ii);
        item = listobject_get(val, ii);
        listobject_set(ob, getintvalue(idx), item);
        DECREF(idx);
        DECREF(item);
    }
    return 1;
}


static int listobject_resize(EmListObject *lo) {
    int newnitems = lo->nitems * 2u; // 50% load
    EmObject ** tmp;
    tmp = (EmObject **) realloc(lo->list, newnitems * sizeof(EmObject *));
    if (tmp == NULL) {
        ex_nomem("no memory to resize list");
        return 0;
    } else {
        size_t newsize, oldsize;
        oldsize = lo->size * sizeof(EmObject *);
        newsize = newnitems * sizeof(EmObject *);
        // Make sure the newly allocated space are filled with zeros.
        memset((char *)tmp + oldsize, 0, newsize - oldsize);
        lo->list = tmp;
        lo->size = newnitems;
    }
    return 1;
}

int listobject_append(EmObject *ob, EmObject *val) {
    EmListObject *lo = (EmListObject *) ob;
    if (lo->nitems * 3 > lo->size * 2) {
        if (listobject_resize(lo) == 0)
            return 0;
    }
    INCREF(val);
    lo->list[lo->nitems] = val;
    lo->nitems++;
    return 1;
}

int listobject_insert(EmObject *ob, int idx, EmObject *val) {
    EmListObject *lo = (EmListObject *)ob;
    if (idx < 0)
        idx += lo->nitems;

    if (idx >= lo->nitems) {
        ex_index("index out of list boundary");
        return 0;
    }
    if (lo->nitems * 3 > lo->size * 2) {
        if (listobject_resize(lo) == 0)
            return 0;
    }
    INCREF(val);
    memmove(lo->list[idx+1], lo->list[idx],
            sizeof(EmObject *) * (lo->nitems - 1 - idx));
    lo->list[idx] = val;
    lo->nitems++;
    return 1;
}

EmObject *listobject_delete(EmObject *ob, int idx) {
    EmListObject *lo = (EmListObject *) ob;
    if (idx < 0)
        idx += lo->nitems;

    if (idx >= lo->nitems) {
        ex_index("index out of list boundary");
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
