#ifndef OBJECT_H
#define OBJECT_H

#define OB_HEAD struct _typeobject *type; \
    int refcnt; \
    int nitems

#define OB_HEAD_INIT(type)      type, 1

#define NEWOBJ(type, typeobj)   ((type *) newobj(typeobj))

#define NEWREF(ob)  (ob)->refcnt = 1
#define INCREF(ob)  (ob)->refcnt++
#define DECREF(ob)  if (--(ob)->refcnt == 0) freeobj(ob)
#define CLRREF(ob)  freeobj(ob)

#define DEL(p)      free(p); (p) = NULL

typedef struct _object {
    OB_HEAD;
} EmObject;


/*
 * Following number, sequence and mapping methods are supposed to be
 * used without function calls. For an example, the number add method
 * is called when an expression "a + b" is encountered.
 * The getattr function is to get the methods of the object can should
 * be called as a function. For an example, sort on a list.
 */

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
    int (*len) (EmObject *);
    EmObject *(*concate) (EmObject *, EmObject *);
    EmObject *(*get) (EmObject *, int);
    EmObject *(*slice) (EmObject *, int, int, int);
    int (*set) (EmObject *, int, EmObject *);
    int (*set_slice) (EmObject *, int, int, int, EmObject *);
} EmSequenceMethods;


/*
 * Methods for mappings like hash
 */
typedef struct {
    int (*len) (EmObject *);
    EmObject *(*get) (EmObject *, EmObject *);
    int (*set) (EmObject *, EmObject *, EmObject *);
} EmMappingMethods;




/*
 * The type object that describe the type of an object
 */
typedef struct _typeobject {
    OB_HEAD;
    char *tp_name;
    size_t tp_size;
    size_t tp_itemsize;

    void (*tp_dealloc)(EmObject *);
    void (*tp_print)(EmObject *, FILE*);
    EmObject *(*tp_tostr)(EmObject *);
    EmObject *(*tp_getattr)(EmObject *, char *);
    int (*tp_setattr)(EmObject *, char *, EmObject *);
    int (*tp_compare)(EmObject *, EmObject *);
    unsigned long (*tp_hashfunc)(EmObject *);
    int (*tp_boolean)(EmObject *);

    EmNumberMethods *tp_as_number;
    EmSequenceMethods *tp_as_sequence;
    EmMappingMethods *tp_as_mapping;
} EmTypeObject;


/*
 * Note the following function are all convenience functions.
 * They are not supposed to be set as function pointers
 * for type object (infinite loop), but rather directly
 * called in other functions.
 */
EmObject *newobj(EmTypeObject *);
void freeobj(EmObject *);
void printobj(EmObject *, FILE *);
EmObject *tostrobj(EmObject *);
EmObject *getattr(EmObject *, char *);
int setattr(EmObject *, char *, EmObject *);
int cmpobj(EmObject *, EmObject *);
unsigned long hashobj(EmObject *);
int boolobj(EmObject *);


extern EmTypeObject Typetype;

/*
 * The string representation output buffer shared by all objects
 */
#define AS_STRING_LENGTH 80
extern char asString[];

extern EmObject nulobj;

#endif
