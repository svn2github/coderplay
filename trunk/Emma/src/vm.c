/*
 * vm.c
 *
 *  Created on: 16/08/2013
 *      Author: ywangd
 */
#include "Emma.h"

#define DEFAULT_VALUESTACK_SIZE     50

#define NEXT_INSTR(co,pc)       (co)->code[pc++]
#define NEXT_ARG(co,pc)         (pc+=2, ((co)->code[pc-1] << 8) + (co)->code[pc-2])

#define PUSH(v)     if (f->vs_top >= f->vs_size) resizevaluestack(f); \
                        f->valuestack[f->vs_top++] = v;
#define POP()       ((f->vs_top <= 0) ? \
                        log_error(MEMORY_ERROR, "value stack underflow") : \
                        f->valuestack[--f->vs_top])

static VM *vm;
static Environment *topenv;

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


void env_free(Environment *env) {
    hashobject_free(env->binding);
    free(env);
}


ExecutionFrame *
newexecutionframe(ExecutionFrame *prev, EmObject *co, Environment *env) {
    ExecutionFrame *f;
    f = (ExecutionFrame *) malloc(sizeof(ExecutionFrame));
    if (f == NULL) {
        log_error(MEMORY_ERROR, "no memory for new execution frame");
        return NULL;
    }
    f->prev = prev;
    f->co = co;
    f->env = env;
    f->pc = 0;
    f->valuestack =
            (EmObject **) malloc(sizeof(EmObject *) * DEFAULT_VALUESTACK_SIZE);
    if (f->valuestack == NULL) {
        DEL(f);
        log_error(MEMORY_ERROR, "no memory for value stack");
        return NULL;
    }
    f->vs_size = DEFAULT_VALUESTACK_SIZE;
    f->vs_top = 0;
    return f;
}

void
resizevaluestack(ExecutionFrame *f) {
    int newsize = f->vs_size + DEFAULT_VALUESTACK_SIZE;
    f->valuestack =
            (EmObject **) realloc(f->valuestack, newsize * sizeof(EmObject *));
    if (f->valuestack == NULL) {
        log_error(MEMORY_ERROR, "no memory to resize value stack");
    } else {
        f->vs_size = newsize;
    }

}

void
executionframe_free(ExecutionFrame *f) {
    freeobj(f->co);
    env_free(f->env);
    DEL(f->valuestack);
}

TryFrame *
newtryframe(TryFrame *prev, ExecutionFrame *f, int pc) {
    TryFrame *t;
    if ((t = (TryFrame *)malloc(sizeof(TryFrame))) == NULL) {
        log_error(MEMORY_ERROR, "no memory for new try frame");
        return NULL;
    }
    t->prev = prev;
    t->f = f;
    t->pc = pc;
}

void tryframe_free(TryFrame *t) {
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
    return 1;
}

void vm_free() {
    ExecutionFrame *f;
    for (f = vm->curframe; f != NULL; f = f->prev) {
        executionframe_free(f);
    }
    TryFrame *t;
    for (t=vm->curtry; t != NULL; t = t->prev) {
        tryframe_free(t);
    }
    DEL(vm);
}

int run_codeobject(EmObject *co, Environment *env) {

    if (env == NULL)
        env = topenv;

    ExecutionFrame *f = newexecutionframe(vm->curframe, co, env);
    vm->curframe = f;


    return 1;
}
