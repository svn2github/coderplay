#include "object.h"
#include "malloc.h"

EmObject * newObject(EmTypeObject *tp) {
    EmObject *ob = (EmObject *) malloc(tp->size);

    GET_type(ob) = tp;
    GET_refcnt(ob) = 1;

    return ob;
}
