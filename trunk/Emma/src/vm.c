/*
 * vm.c
 *
 *  Created on: 16/08/2013
 *      Author: ywangd
 */
#include "Emma.h"

#define DEFAULT_VALUESTACK_SIZE     50

static VM *vm;
Environment *topenv;

Environment *
newenv(Environment *parent) {
    Environment *e = (Environment *) malloc(sizeof(Environment));
    if (e == NULL) {
        log_error(MEMORY_ERROR, "no memory for new environment");
        return NULL;
    }
    e->parent = parent;
    if ((e->binding = newhashobject()) == NULL) {
        DEL(e);
        log_error(MEMORY_ERROR, "no memory for environment binding");
        return NULL;
    }
    return e;
}

EmObject *
env_get(Environment *env, EmObject *name) {
    EmObject *val;
    do {
        val = hashobject_lookup(env->binding, name);
        if (val == NULL)
            env = env->parent;
        else
            return val;
    } while(env != NULL);
    return NULL;
}

void env_set(Environment *env, EmObject *name, EmObject *val) {
    env->binding = hashobject_insert(env->binding, name, val);
}

void env_free(Environment *env) {
    hashobject_free(env->binding);
    free(env);
}

ExecutionFrame *
newexecutionframe(ExecutionFrame *prev, EmCodeObject *co, Environment *env) {
    ExecutionFrame *f;
    f = (ExecutionFrame *) malloc(sizeof(ExecutionFrame));
    if (f == NULL) {
        log_error(MEMORY_ERROR, "no memory for new execution frame");
        return NULL;
    }
    f->prev = prev;
    f->co = co;
    f->env = env;
    f->valuestack = (EmObject **) malloc(
            sizeof(EmObject *) * DEFAULT_VALUESTACK_SIZE);
    if (f->valuestack == NULL) {
        DEL(f);
        log_error(MEMORY_ERROR, "no memory for value stack");
        return NULL;
    }
    f->vs_size = DEFAULT_VALUESTACK_SIZE;
    f->vs_top = 0;
    return f;
}

void resizevaluestack(ExecutionFrame *f) {
    int newsize = f->vs_size + DEFAULT_VALUESTACK_SIZE;
    f->valuestack = (EmObject **) realloc(f->valuestack,
            newsize * sizeof(EmObject *));
    if (f->valuestack == NULL) {
        log_error(MEMORY_ERROR, "no memory to resize value stack");
    } else {
        f->vs_size = newsize;
    }
}

void executionframe_free(ExecutionFrame *f) {
    if (f == NULL)
        return;
    if (f->prev != NULL)
        executionframe_free(f->prev);
    freeobj((EmObject *) f->co);
    env_free(f->env);
    DEL(f->valuestack);
    DEL(f);
}

TryFrame *
newtryframe(TryFrame *prev, ExecutionFrame *f, int pc) {
    TryFrame *t;
    if ((t = (TryFrame *) malloc(sizeof(TryFrame))) == NULL) {
        log_error(MEMORY_ERROR, "no memory for new try frame");
        return NULL;
    }
    t->prev = prev;
    t->f = f;
    t->pc = pc;
}

void tryframe_free(TryFrame *t) {
    if (t == NULL)
        return;
    if (t->prev != NULL)
        tryframe_free(t->prev);
    DEL(t);
}

int vm_init() {
    if ((vm = (VM *) malloc(sizeof(VM))) == NULL) {
        log_error(MEMORY_ERROR, "no memory for virtual machine");
        return 0;
    }
    vm->curframe = NULL;
    vm->curtry = NULL;

    if ((topenv = newenv(NULL)) == NULL) {
        DEL(vm);
        return 0;
    }

    /*
     * Default variables in topenv
     */
    EmObject *name, *val;
    name = newstringobject("stdout");
    val = newfileobject(stdout, "stdout");
    env_set(topenv, name, val);
    DECREF(name);
    DECREF(val);

    /*
     * bltin methods
     */
    bltin_init();

    return 1;
}

void vm_free() {
    executionframe_free(vm->curframe);
    tryframe_free(vm->curtry);
    DEL(vm);
}


EmObject *
add(EmObject *u, EmObject *v) {
    if (u->type->tp_as_number != NULL) {
        return (*u->type->tp_as_number->add)(u,v);
    } else if (u->type->tp_as_sequence != NULL) {
        return (*u->type->tp_as_sequence->concate)(u,v);
    } else {
        log_error(TYPE_ERROR, "operator + not supported for operands");
        return NULL;
    }
}

EmObject *
run_codeobject(EmCodeObject *co, Environment *env) {


#define NEXT_OPCODE()           (co)->code[pc++]
#define NEXT_ARG()              (pc+=2, ((co)->code[pc-1] << 8) + (co)->code[pc-2])
#define HASARG(opcode)          opcode>OP_HASARG?1:0

#define PUSH(v)     if (f->vs_top >= f->vs_size) resizevaluestack(f); \
                        f->valuestack[f->vs_top++] = v;

#define POP()       ((f->vs_top <= 0) ? \
                        log_error(MEMORY_ERROR, "value stack underflow") : \
                        f->valuestack[--f->vs_top])

#define GET_CONST(i)    listobject_get(co->consts,i)
#define GET_NAME(i)     listobject_get(co->names,i)


    int ii;
    EmObject *u, *v, *w, *ob;

    if (env == NULL)
        env = topenv;

    ExecutionFrame *f = newexecutionframe(vm->curframe, co, env);
    vm->curframe = f;
    int pc = 0;
    int opcode, arg;

    /*
     * Variables obtained from POP() requires DECREF if it is no
     * longer needed. Variables pushed with PUSH() mostly do NOT
     * need INCREF because the refcnt usually increased already
     * when the variable is obtained from somewhere else, e.g.
     * consts list, env.
     */
    while (1) {
        opcode = NEXT_OPCODE();
        if (HASARG(opcode))
        arg = NEXT_ARG();

        switch (opcode) {
            case OP_END:
                /*
                 * If code reaches OP_END, it means not return statement has been
                 * ran (otherwise, the code will return before reaching OP_END).
                 * If the code does not belong to top level frame, it must return
                 * a value even when the user does not specify one. In this case,
                 * we return a null object.
                 */
                if (f->prev != NULL) {
                    return &nulobj;
                } else {
                    return NULL;
                }
                break;

            case OP_ADD:
                v = POP();
                u = POP();
                w = add(u, v);
                PUSH(w);
                DECREF(u);
                DECREF(v);
                break;

            case OP_PUSHC:
                v = GET_CONST(arg);
                PUSH(v);
                break;

            case OP_PUSH:
                u = GET_NAME(arg);
                v = env_get(f->env, u);
                PUSH(v);
                DECREF(u);
                break;

            case OP_PUSHN:
                v = GET_NAME(arg);
                PUSH(v);
                break;

            case OP_POP:
                u = GET_NAME(arg);
                v = POP();
                env_set(f->env, u, v);
                DECREF(u);
                DECREF(v);
                break;

            case OP_MKLIST:
                ob = newlistobject_of_null(arg);
                for (ii=0;ii<arg;ii++) {
                    v = POP();
                    listobject_set(ob, arg-1-ii, v);
                    DECREF(v);
                }
                PUSH(ob);
                break;

            case OP_MKHASH:
                w = newhashobject_from_size(arg);
                for (ii=0; ii<2*arg; ii+=2) {
                    v = POP();
                    u = POP();
                    w = hashobject_insert(w, u, v);
                    DECREF(u);
                    DECREF(v);
                }
                PUSH(w);
                break;

            case OP_PRINT:
                v = POP(); // list
                u = POP(); // destination
                for (ii=0;ii<v->nitems;ii++) {
                    w = listobject_get(v,ii);
                    printobj(w, ((EmFileObject *)u)->fp);
                    DECREF(w);
                }
                fprintf(getfp(u), "\n");
                DECREF(u);
                DECREF(v);
                break;


            case OP_CALL:
                v = POP(); // the params list
                u = POP(); // the func
                EmObject *retval;
                if (u->type == &Bltinmethodtype) {
                    retval = (*((EmBltinmethodObject *)u)->method)(NULL, v);
                }
                PUSH(retval);
                DECREF(u);
                DECREF(v);
                break;

            case OP_GET_INDEX:
                u = POP(); // the index, must be integer
                w = POP(); // the list/hash object
                if (is_EmListObject(w))
                    v = listobject_get(w, getintvalue(u));
                else
                    v = hashobject_lookup(w, u);
                PUSH(v);
                DECREF(u);
                DECREF(w);
                break;

            case OP_SET_INDEX:
                u = POP(); // the index, must be integer
                w = POP(); // the list/hash object
                v = POP(); // the value
                if (is_EmListObject(w))
                    listobject_set(w, getintvalue(u), v);
                else
                    hashobject_insert(w, u, v);
                DECREF(u);
                DECREF(v);
                DECREF(w);
                break;

            default:
                printf("unhandled OP code\n");
                break;
        }

    }

    return NULL;
}
