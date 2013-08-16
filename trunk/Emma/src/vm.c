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

int vm_init() {

    return 1;
}

void vm_free() {

}

int run_codeobject(EmObject *co) {

    return 1;
}
