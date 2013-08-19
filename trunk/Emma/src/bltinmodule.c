/*
 * bltinmodule.c
 *
 *  Created on: 19/08/2013
 *      Author: ywang@gmail.com
 */
#include "Emma.h"

static int check_params(BltinmethodParamsDesc *desc, EmObject *ob) {

    int ret, npparams, haskeywords;
    EmObject *keywords, *pparams;

    if (ob == &nulobj) {
        if (desc->nreq_args > 0)
            return 0;
        else
            return 1;
    }

    pparams = listobject_get(ob, 0);
    keywords = listobject_get(ob, 1);

    npparams = listobject_len(pparams);
    if (npparams > desc->nargs && desc->nargs >= 0) {
        log_error(RUNTIME_ERROR, "incorrect number of arguments");
        ret = 0;
    }
    if (npparams < desc->nreq_args) {
        log_error(RUNTIME_ERROR, "fewer arguments than required");
        ret = 0;
    }
    DECREF(pparams);

    if (keywords != &nulobj) {
        EmObject *keylist, *kw;
        keylist = hashobject_keys(keywords);
        char *match;
        int ii;
        for (ii = 0; ii < listobject_len(keylist); ii++) {
            kw = listobject_get(keywords, ii);
            match = strstr(desc->keywords, getstringvalue(kw));
            DECREF(kw);
            if (match == NULL) {
                log_error(RUNTIME_ERROR, "unknown keyword parameter");
                ret = 0;
            }
        }
        DECREF(keylist);
    }
    DECREF(keywords);

    return ret;
}

EmObject *
bltin_list(EmObject *self, EmObject *v) {
    static BltinmethodParamsDesc desc = { -1, 0, "size", };
    EmObject *keywords, *pparams;
    EmObject *kw, *item;
    EmObject *ret;
    int ii, size;

    if (check_params(&desc, v) == 0) {
        return NULL;
    }

    if (v == &nulobj) {
        ret = newlistobject(0);
    } else {
        pparams = listobject_get(v, 0);
        keywords = listobject_get(v, 1);
        size = listobject_len(pparams);
        if (keywords != &nulobj) {
            kw = hashobject_lookup_by_string(keywords, "size");
            if (kw != NULL) {
                if (size < ((EmIntObject *) kw)->ival) {
                    size = ((EmIntObject *) kw)->ival;
                }
                DECREF(kw);
            }
        }
        ret = newlistobject_of_null(size);
        for (ii=0;ii<listobject_len(pparams);ii++) {
            item = listobject_get(pparams, ii);
            listobject_set(ret, ii, item);
            DECREF(item);
        }
        DECREF(pparams);
        DECREF(keywords);
    }

    return ret;
}

EmObject *
bltin_hash(EmObject *lo) {
    int size = listobject_len(lo);
    if (size % 2 != 0) {
        log_error(RUNTIME_ERROR, "incorrect number of parameters for hash");
        return NULL;
    }
    return NULL;
}

static Methodlist bltin_methods[] = {
        {"list", bltin_list},
        {NULL, NULL},
};

void bltin_init() {
    Methodlist *ml;
    EmObject *v;
    for (ml = bltin_methods; ml->name != NULL; ml++) {
        v = newbltinmethodobject(ml->name, ml->meth, NULL);
        topenv->binding = hashobject_insert_by_string(topenv->binding, ml->name, v);
        DECREF(v);
    }
}



