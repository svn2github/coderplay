#include "object.h"

typedef struct {
    EmObject *key;
    EmObject *val;
} hashentry;

typedef struct _hashobject {
    EmContainerObject _;
    int length;
    int loadFactor;
    hashentry *table;
} EmHashObject;


EmTypeObject Hashtype = {
    OB_HEAD_INIT(&Typetype), 
    "hash",
    sizeof(EmHashObject),
    0,
    0,
};

EmObject * newhashobject() {
}
