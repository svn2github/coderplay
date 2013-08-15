/*
 * codeobject.c
 *
 *  Created on: 15/08/2013
 *      Author: ywangd
 */

#include "allobject.h"
#include "opcode.h"

EmObject *
newcodeobject(int nbytes) {
    EmCodeObject *co;
    if ((co = NEWOBJ(EmCodeObject, &Codetype)) == NULL) {
        log_error(MEMORY_ERROR, "no memory for new code object");
        return NULL;
    }
    if ((co->code = (unsigned char *) malloc(sizeof(unsigned char) * nbytes)) == NULL) {
        DEL(co);
        log_error(MEMORY_ERROR, "no memory for code string in code object");
        return NULL;
    }
    co->nbytes = nbytes;
    co->consts = NULL;
    co->names = NULL;

    return (EmObject *) co;
}

void codeobject_free(EmObject *ob) {
    EmCodeObject *co = (EmCodeObject *) ob;
    freeobj(co->consts);
    freeobj(co->names);
    DEL(co->code);
    DEL(co)
    ;
}

int codeobject_compare(EmObject *a, EmObject *b) {
    EmCodeObject *u = (EmCodeObject *) a;
    EmCodeObject *v = (EmCodeObject *) b;

    int res;
    res = strcmp(u->code, v->code);
    if (res != 0)
        return res;

    res = cmpobj(u->consts, v->consts);
    if (res != 0)
        return res;

    return cmpobj(u->names, v->names);

}


void codeobject_print(EmObject *ob, FILE *fp) {
    EmCodeObject *co = (EmCodeObject *) ob;
    int opcode, arg, count = 0;
    EmObject *m;

    while (count < co->nbytes) {
        opcode = co->code[count];
        fprintf(fp, "%5d %-20s", count++, opcode_types[opcode]);
        if (opcode > OP_HASARG) {
            count += 2;
            arg = (co->code[count - 1] << 8) + co->code[count - 2];
            fprintf(fp, "%d ", arg);
            if (opcode == OP_PUSHC) {
                m = listobject_get(co->consts, arg);
                fprintf(fp, "(%s)", tostrobj(m));
                DECREF(m);
            } else if (opcode == OP_PUSH || opcode == OP_POP) {
                m = listobject_get(co->names, arg);
                fprintf(fp, "(%s)", tostrobj(m));
                DECREF(m);
            }
        }
        fprintf(fp, "\n");
    }
}



EmTypeObject Codetype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "code",                         // tp_name
        sizeof(EmCodeObject),           // tp_size
        0,                              // tp_itemsize

        codeobject_free,                // tp_dealloc
        codeobject_print,               // tp_print
        0,                              // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        codeobject_compare,             // tp_compare
        0,                              // tp_hashfunc

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

