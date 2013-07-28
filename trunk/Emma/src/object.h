#ifndef OBJECT_H
#define OBJECT_H

#define OB_HEAD struct _typeobject *type; \
    unsigned int refcnt; \
    struct _object *base; \
    unsigned int nitems

#define OB_HEAD_INIT(p_type) p_type, 1


typedef struct _object {
    OB_HEAD;
} EmObject;

typedef struct {
    EmObject *(*add) (EmObject *, EmObject *);
} EmNumberMethods;

typedef struct {
    unsigned int (*length) (EmObject *);
    EmObject *(*concate) (EmObject *, EmObject *);
} EmSequenceMethods;

typedef struct {
    unsigned int (*length) (EmObject *);
    EmObject *(*subscript) (EmObject *, EmObject *);
}EmMappingMethods;

typedef struct _typeobject {
    OB_HEAD;
    char *tp_name;
    unsigned int tp_size;
    unsigned int tp_itemsize;

    EmObject *(*tp_alloc)();
    void (*tp_dealloc)(EmObject *);
    void (*tp_print)(EmObject *, FILE*);
    EmObject *(*tp_str)(EmObject *);
    EmObject *(*tp_getattr)(EmObject *, char *);
    int (*tp_setattr)(EmObject *, char *, EmObject *);
    int (*tp_compare)(EmObject *, EmObject *);
    long (*tp_hashfunc)(EmObject *);

    EmNumberMethods *tp_as_number;
    EmSequenceMethods *tp_as_sequence;
    EmMappingMethods *tp_as_mapping;


} EmTypeObject;


#endif
