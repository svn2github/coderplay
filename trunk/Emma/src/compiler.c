/*
 * compiler.c
 *
 *  Created on: 12/08/2013
 *      Author: ywangd
 */
#include "compiler.h"

Compiled *
newcompiled() {

    Compiled *com = (Compiled *)malloc(sizeof(Compiled));
    if (com == NULL) {
        return log_error(MEMORY_ERROR, "not enough memory to create new compiled");
    }

    com->code = NULL;

    if ((com->consts = newlistobject(0)) == NULL) {
        DEL(com);
        return log_error(MEMORY_ERROR, "not enough memory to create consts of compiled");
    }

    if ((com->names = newlistobject(0)) == NULL) {
        DEL(com->consts);
        DEL(com);
        return log_error(MEMORY_ERROR, "not enough memory to create names of compiled");
    }

    com->nexti = 0;
    return com;
}


Compiled *
compile_stree(AstNode *stree) {
    return NULL;
}
