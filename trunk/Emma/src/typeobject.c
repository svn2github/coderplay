#include <stdlib.h>
#include "object.h"

EmTypeObject Typetype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // base
        0,                              // nitems
        "type",                         // tp_name
        sizeof(EmTypeObject),           // tp_size
        0,                              // tp_itemsize

        0,                              // tp_alloc
        0,                              // tp_dealloc
        0,                              // tp_print
        0,                              // tp_str
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        0,                              // tp_hashfunc

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

