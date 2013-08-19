/*
 * bltinmodule.c
 *
 *  Created on: 19/08/2013
 *      Author: ywang@gmail.com
 */
#include "Emma.h"

static int
check_params(BltinmethodParamsDesc *desc, EmObject *ob) {

    int ret = 1;

    EmListObject *lo = (EmListObject *)listobject_get(ob, 0);
    if (lo->nitems > desc->nargs && desc->nargs >= 0) {
        log_error(RUNTIME_ERROR, "incorrect number of arguments");
        ret = 0;
    }
    if(lo->nitems < desc->nreq_args) {
        log_error(RUNTIME_ERROR, "fewer arguments than required");
        ret = 0;
    }
    DECREF((EmObject *)lo);

    EmObject *ho = listobject_get(ob, 1);
    EmObject *keywords = hashobject_keys(ho);
    EmObject *kw;
    char *match;
    int ii;
    for (ii=0;ii<listobject_len(keywords);ii++) {
        kw = listobject_get(keywords, ii);
        match = strstr(desc->keywords, getstringvalue(kw));
        DECREF(kw);
        if (match == NULL) {
            log_error(RUNTIME_ERROR, "unknown keyword parameter");
            ret = 0;
        }
    }
    DECREF(keywords);
    DECREF(ho);

    return ret;
}

EmObject *
bltin_list(EmObject *self, EmObject *v) {
    static BltinmethodParamsDesc desc = {
            -1,
            0,
            "size",
    };
    if (check_params(&desc, v) == 0) {
        return NULL;
    }

    EmObject *lo = listobject_get(v, 0);
    EmObject *ho = listobject_get(v, 1);



    return NULL;
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

