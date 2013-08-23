/*
 * vm.h
 *
 *  Created on: 16/08/2013
 *      Author: ywangd
 */

#ifndef VM_H_
#define VM_H_

typedef struct _environment {
    struct _environment *parent;
    // hash object that saves the bindings, i.e. name and the content the
    // the name points to.
    EmObject *binding;
} Environment;

typedef struct _execution_frame {
    struct _execution_frame *prev;
    EmCodeObject *co;
    Environment *env;
    EmObject **valuestack;
    int vs_size; // size of the value stack
    int vs_top;  // the top idx of value stack
    int cur_row;
} ExecutionFrame;

typedef struct _try_frame {
    struct _try_frame *prev;
    ExecutionFrame *f;
    int pc;
} TryFrame;

typedef struct _vm {
    ExecutionFrame *curframe;   // currently running frame
    int nframes;
    TryFrame *curtry; // currently working try frame
    Environment *topenv; // user code is running in descent of topenv
} VM;

extern VM *vm;

Environment *newenv(Environment *parent);
void env_free(Environment *env);

EmObject* run_codeobject(EmCodeObject *co, Environment *env, EmObject *args);



#endif /* VM_H_ */
