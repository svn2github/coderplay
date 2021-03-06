/*
 * bltinmodule.c
 *
 *  Created on: 19/08/2013
 *      Author: ywang@gmail.com
 */
#include "Emma.h"

static int check_params(BltinmethodParamsDesc *desc, EmObject *ob) {

    int retval = 1, npparams, haskeywords;
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
        ex_runtime("incorrect number of arguments");
        retval = 0;
    }
    if (npparams < desc->nreq_args) {
        ex_runtime("fewer arguments than required");
        retval = 0;
    }
    DECREF(pparams);

    if (keywords != &nulobj) {
        EmObject *keylist, *kw;
        keylist = hashobject_keys(keywords);
        char *match;
        int ii;
        for (ii = 0; ii < listobject_len(keylist); ii++) {
            kw = listobject_get(keylist, ii);
            match = strstr(desc->keywords, getstringvalue(kw));
            DECREF(kw);
            if (match == NULL) {
                ex_runtime("unknown keyword parameter");
                retval = 0;
            }
        }
        DECREF(keylist);
    }
    DECREF(keywords);

    return retval;
}

EmObject *
bltin_list(EmObject *self, EmObject *v) {
    static BltinmethodParamsDesc desc = { -1, 0, "size value", };
    EmObject *pparams, *keywords;
    EmObject *kw, *item;
    EmObject *retval;
    int ii, size;

    if (check_params(&desc, v) == 0) {
        return NULL;
    }

    if (v == &nulobj) {
        retval = newlistobject(0);
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
        retval = newlistobject_of_null(size);
        if (keywords != &nulobj) {
            kw = hashobject_lookup_by_string(keywords, "value");
            if (kw != NULL) {
                for (ii=0;ii<listobject_len(retval);ii++) {
                    listobject_set(retval, ii, kw);
                }
                DECREF(kw);
            }
        }
        for (ii=0;ii<listobject_len(pparams);ii++) {
            item = listobject_get(pparams, ii);
            listobject_set(retval, ii, item);
            DECREF(item);
        }
        DECREF(pparams);
        DECREF(keywords);
    }

    return retval;
}

EmObject *
bltin_hash(EmObject *self, EmObject *v) {
    static BltinmethodParamsDesc desc = { -1, 0, ""};

    if (check_params(&desc, v) == 0) {
        return NULL;
    }

    EmObject *retval;
    EmObject *pparams;

    if (v == &nulobj) {
        retval = newhashobject();
    } else {
        pparams = listobject_get(v, 0);
        retval = newhashobject_from_list(pparams);
        DECREF(pparams);
    }

    return retval;
}

static Methodlist bltin_methods[] = {
        {"list", bltin_list},
        {"hash", bltin_hash},
        {NULL, NULL},
};

EmObject *MemoryException;
EmObject *SystemException;
EmObject *TypeException;
EmObject *KeyException;
EmObject *IndexException;
EmObject *RuntimeException;

EmObject *last_exception = NULL;

EmObject *initerror(Environment *env, char *type, char *message) {
    int ok;
    EmObject *eo;

    eo = newexceptionobject(type, message);
    if (eo == NULL)
        return NULL;

    ok = env_set_by_string(env, type, eo);

    if (ok) {
        DECREF(eo);
        return eo;
    } else {
        DECREF(eo);
        return NULL;
    }
}

void bltin_init(Environment *env) {
    Methodlist *ml;
    EmObject *v;

    for (ml = bltin_methods; ml->name != NULL; ml++) {
        v = newbltinmethodobject(ml->name, ml->meth, NULL);
        env_set_by_string(env, ml->name, v);
        DECREF(v);
    }

    MemoryException = initerror(env, "MemoryException", "no memory");
    SystemException =initerror(env, "SystemException", "internal error");
    TypeException = initerror(env, "TypeException", "wrong type");
    KeyException = initerror(env, "KeyException", "invalid key");
    IndexException = initerror(env, "IndexException", "invalid index");
    RuntimeException = initerror(env, "RuntimeException", "runtime error");
}



