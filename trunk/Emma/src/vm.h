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
    EmObject *co;
    Environment *env;
    int pc;
    EmObject **valuestack;
    int vs_size; // size of the value stack
    int vs_top;  // the top idx of value stack
} ExecutionFrame;

typedef struct _vm {
    ExecutionFrame *callstack; // call frame stack
    ExecutionFrame *trystack; // try/catch frame stack
} VM;


int run_codeobject(EmCodeObject *co);



#endif /* VM_H_ */
