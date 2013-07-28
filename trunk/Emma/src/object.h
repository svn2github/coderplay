#ifndef OBJECT_H
#define OBJECT_H

#define OB_HEAD struct _typeobject *type; \
    unsigned int refcnt; \
    struct _object *base; \
    unsigned int nitems

#define OB_HEAD_INIT(type) type, 1


typedef struct _object {
    OB_HEAD;
} EmObject;

/*
 * A series of methods that operate on numbers
 */
typedef struct {
    EmObject *(*add) (EmObject *, EmObject *);
    EmObject *(*sub) (EmObject *, EmObject *);
    EmObject *(*mul) (EmObject *, EmObject *);
    EmObject *(*div) (EmObject *, EmObject *);
    EmObject *(*mod) (EmObject *, EmObject *);
    EmObject *(*pow) (EmObject *, EmObject *);
    EmObject *(*neg) (EmObject *);
} EmNumberMethods;


/*
 * Methods for sequences like list and string
 */
typedef struct {
    unsigned int (*length) (EmObject *);
    EmObject *(*concate) (EmObject *, EmObject *);
    EmObject *(*subscript) (EmObject *, int);
    EmObject *(*slice) (EmObject *, int, int, int);
} EmSequenceMethods;


/*
 * Methods for mappings like hash
 */
typedef struct {
    unsigned int (*length) (EmObject *);
    EmObject *(*subscript) (EmObject *, EmObject *);
}EmMappingMethods;


/*
 * The type object that describe the type of an object
 */
typedef struct _typeobject {
    OB_HEAD;
    char *tp_name;
    unsigned int tp_size;
    unsigned int tp_itemsize;

    EmObject *(*tp_alloc)();
    void (*tp_dealloc)(EmObject *);
    void (*tp_print)(EmObject *, FILE*);
    char *(*tp_str)(EmObject *);
    EmObject *(*tp_getattr)(EmObject *, char *);
    int (*tp_setattr)(EmObject *, char *, EmObject *);
    int (*tp_compare)(EmObject *, EmObject *);
    long (*tp_hashfunc)(EmObject *);

    EmNumberMethods *tp_as_number;
    EmSequenceMethods *tp_as_sequence;
    EmMappingMethods *tp_as_mapping;
} EmTypeObject;

extern void object_print(EmObject *, FILE *);
extern void object_str(EmObject *);
extern EmObject *object_getattr(EmObject *, char *);
extern int object_setattr(EmObject *, char *, EmObject *);
extern int object_compare(EmObject *, EmObject *);
extern long object_hashfunc(EmObject *);

/*
 * The string representation output buffer shared by all objects
 */
#define AS_STRING_LENGTH 80
extern char *asString;


#endif
