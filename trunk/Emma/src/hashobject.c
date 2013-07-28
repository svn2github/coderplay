#include "object.h"

typedef struct {
    EmObject *key;
    EmObject *val;
} hashentry;

typedef struct _hashobject {
    OB_HEAD;
    int length;
    int loadFactor;
    hashentry *table;
} EmHashObject;


EmTypeObject Hashtype = {
        OB_HEAD_INIT(&Typetype),
        "hash",
        0,
        sizeof(EmHashObject),
        0,
        0,
};

EmObject * newhashobject() {
    return 0;
}
