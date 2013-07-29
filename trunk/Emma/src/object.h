#ifndef OBJECT_H
#define OBJECT_H

#define OB_HEAD struct _typeobject *type; \
    unsigned int refcnt; \
    struct _object *base; \
    unsigned int nitems

#define OB_HEAD_INIT(type) type, 1

#define OBJECT_NEW(type, typeobj) ((type *) object_new(typeobj))

#define OBJECT_FREE(ob) if (ob->type->tp_dealloc) { \
            ob->type->tp_dealloc(ob); \
        } else { \
            log_error(SYSTEM_ERROR, "object cannot be freed"); \
        }

#define INCREF(ob) ob->refcnt++
#define DECREF(ob) if (--ob->refcnt == 0) OBJECT_FREE(ob)


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


/*
 * Following function can be used as placeholders for type object's
 * function pointers.
 */
extern void object_print(EmObject *, FILE *);
extern void object_str(EmObject *);

/*
 * Note the following function are all generic functions.
 * They are not supposed to be set as function pointers
 * for type object (infinite loop), but rather directly
 * called in other functions.
 */
extern EmObject *getattr(EmObject *, char *);
extern int setattr(EmObject *, char *, EmObject *);
extern int cmpobj(EmObject *, EmObject *);
extern long hashobj(EmObject *);

/*
 * The string representation output buffer shared by all objects
 */
#define AS_STRING_LENGTH 80
extern char *asString;

extern EmObject nulobj;

#endif
