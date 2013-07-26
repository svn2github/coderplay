#ifndef OBJECT_H
#define OBJECT_H

#define OB_HEAD_INIT(p_type) {p_type, 1,}

#define GET_type(ob) (EmObject *)(ob)->type
#define GET_refcnt(ob) (EmObject *)(ob)->refcnt

typedef struct _object {
    struct _typeobject *type;
    unsigned int refcnt;
} EmObject;

typedef struct _containerobject {
    EmObject _;
    unsigned int nitems;
} EmContainerObject;

typedef struct _typeobject {
    EmObject _;
    char *type_name;
    unsigned int size;

    void (*dealloc) (EmObject *);

    long (*hashfunc) (EmObject *);

} EmTypeObject;





#endif
