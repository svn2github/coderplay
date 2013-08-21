/*
 * vm.c
 *
 *  Created on: 16/08/2013
 *      Author: ywangd
 */
#include "Emma.h"

#define DEFAULT_VALUESTACK_SIZE     50

VM *vm;

Environment *
newenv(Environment *parent) {
    Environment *e = (Environment *) malloc(sizeof(Environment));
    if (e == NULL) {
        ex_mem("no memory for new environment");
        return NULL;
    }
    e->parent = parent;
    if ((e->binding = newhashobject()) == NULL) {
        DEL(e);
        ex_mem("no memory for environment binding");
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

int env_set(Environment *env, EmObject *name, EmObject *val) {
    return hashobject_insert(env->binding, name, val);
}

int env_set_by_string(Environment *env, char *name, EmObject *val) {
    EmObject *nameob;
    int retval;
    nameob = newstringobject(name);
    retval = env_set(env, nameob, val);
    DECREF(nameob);
    return retval;
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
        ex_mem("no memory for new execution frame");
        return NULL;
    }
    f->prev = prev;
    f->co = co;
    f->env = env;
    f->valuestack = (EmObject **) malloc(
            sizeof(EmObject *) * DEFAULT_VALUESTACK_SIZE);
    if (f->valuestack == NULL) {
        DEL(f);
        ex_mem("no memory for value stack");
        return NULL;
    }
    f->vs_size = DEFAULT_VALUESTACK_SIZE;
    f->vs_top = 0;
    return f;
}

int resizevaluestack(ExecutionFrame *f) {
    int newsize = f->vs_size + DEFAULT_VALUESTACK_SIZE;

    f->valuestack = (EmObject **) realloc(f->valuestack,
            newsize * sizeof(EmObject *));

    if (f->valuestack == NULL) {
        ex_mem("no memory to resize value stack");
        return 0;
    }

    f->vs_size = newsize;
    return 1;
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
        ex_mem("no memory for new try frame");
        return NULL;
    }
    t->prev = prev;
    t->f = f;
    t->pc = pc;
    return t;
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
        ex_mem("no memory for virtual machine");
        return 0;
    }
    vm->curframe = NULL;
    vm->curtry = NULL;

    if ((vm->topenv = newenv(NULL)) == NULL) {
        DEL(vm);
        return 0;
    }

    /*
     * Default variables in topenv
     */
    EmObject *name, *val;
    name = newstringobject("stdout");
    val = newfileobject(stdout, "stdout");
    env_set(vm->topenv, name, val);
    DECREF(name);
    DECREF(val);

    /*
     * bltin methods
     */
    bltin_init(vm->topenv);

    return 1;
}

void vm_free() {
    executionframe_free(vm->curframe);
    tryframe_free(vm->curtry);
    env_free(vm->topenv);
    DEL(vm);
}


EmObject *
add(EmObject *u, EmObject *v) {
    if (u->type->tp_as_number != NULL) {
        return (*u->type->tp_as_number->add)(u,v);
    } else if (u->type->tp_as_sequence != NULL) {
        return (*u->type->tp_as_sequence->concate)(u,v);
    } else {
        ex_type("operator + not supported for operands");
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
                        NULL : \
                        f->valuestack[--f->vs_top])

#define N_VSTACK()  f->vs_top

#define GET_CONST(i)    listobject_get(co->consts,i)
#define GET_NAME(i)     listobject_get(co->names,i)


    int ii, ok = 1;
    EmObject *u, *v, *w, *x = &nulobj;
    EmObject *retval;
    int pc = 0;
    int opcode, arg;

    if (env == NULL)
        env = newenv(vm->topenv);

    ExecutionFrame *f = newexecutionframe(vm->curframe, co, env);
    vm->curframe = f;

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
                x = add(u, v);
                PUSH(x);
                DECREF(u);
                DECREF(v);
                break;

            case OP_PUSHC:
                x = GET_CONST(arg);
                PUSH(x);
                break;

            case OP_PUSH:
                u = GET_NAME(arg);
                x = env_get(f->env, u);
                PUSH(x);
                DECREF(u);
                break;

            case OP_PUSHN:
                x = GET_NAME(arg);
                PUSH(x);
                break;

            case OP_POP:
                u = GET_NAME(arg);
                v = POP();
                ok = env_set(f->env, u, v);
                DECREF(u);
                DECREF(v);
                break;

            case OP_MKLIST:
                x = newlistobject_of_null(arg);
                for (ii=0;ii<arg;ii++) {
                    v = POP();
                    ok = listobject_set(x, arg-1-ii, v);
                    DECREF(v);
                }
                PUSH(x);
                break;

            case OP_MKHASH:
                x = newhashobject_from_size(arg);
                for (ii=0; ii<2*arg; ii+=2) {
                    v = POP();
                    u = POP();
                    ok = hashobject_insert(x, u, v);
                    DECREF(u);
                    DECREF(v);
                }
                PUSH(x);
                break;

            case OP_PRINT:
                v = POP(); // list
                u = POP(); // destination
                for (ii=0;ii<v->nitems;ii++) {
                    w = listobject_get(v,ii);
                    printobj(w, getfp(u));
                    fprintf(getfp(u), " ");
                    DECREF(w);
                }
                fprintf(getfp(u), "\n");
                DECREF(u);
                DECREF(v);
                break;

            case OP_CALL:
                v = POP(); // the params list
                u = POP(); // the func
                if (u->type == &Bltinmethodtype) {
                    x = (*((EmBltinmethodObject *)u)->method)(NULL, v);
                }
                PUSH(x);
                DECREF(u);
                DECREF(v);
                break;

            case OP_GET_INDEX:
                u = POP(); // the index, must be integer
                w = POP(); // the list/hash object
                if (is_EmListObject(w))
                    x = listobject_get(w, getintvalue(u));
                else
                    x = hashobject_lookup(w, u);
                PUSH(x);
                DECREF(u);
                DECREF(w);
                break;

            case OP_GET_SLICE:
                u = POP(); // the slice list, 3 elements
                w = POP(); // the list object
                x =listobject_slice_by_list(w, u);
                PUSH(x);
                DECREF(u);
                DECREF(w);
                break;

            case OP_GET_IDXLIST:
                u = POP(); // the idxlist
                w = POP(); // the list object
                x = listobject_idxlist(w, u);
                PUSH(x);
                DECREF(u);
                DECREF(w);
                break;

            case OP_SET_INDEX:
                u = POP(); // the index, must be integer
                w = POP(); // the list/hash object
                v = POP(); // the value
                if (is_EmListObject(w))
                    ok = listobject_set(w, getintvalue(u), v);
                else
                    ok = hashobject_insert(w, u, v);
                DECREF(u);
                DECREF(v);
                DECREF(w);
                break;

            case OP_SET_SLICE:
                u = POP(); // the slice list
                w = POP(); // the list object
                v = POP(); // the value
                ok = listobject_set_slice(w, u, v);
                DECREF(u);
                DECREF(v);
                DECREF(w);
                break;

            case OP_SET_IDXLIST:
                u = POP(); // the idxlist
                w = POP(); // the list object
                v = POP(); // the value
                ok = listobject_set_idxlist(w, u, v);
                DECREF(u);
                DECREF(v);
                DECREF(w);
                break;

            default:
                ex_system_with_val("Unknown opcode", opcode_types[opcode]);
                ok = 0;
                break;
        } // endswitch

        // Check for exception
        if (x == NULL || ok == 0) {
            print_exception();
            clear_exception();
            retval = NULL;
            while (N_VSTACK() != 0) {
                x = POP();
                if (x != NULL)
                    DECREF(x);
            }
            x = &nulobj;
            ok = 1;
            break;
        }

    } // endwhile

    return retval;
}
