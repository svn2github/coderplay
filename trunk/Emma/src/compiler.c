/*
 * compiler.c
 *
 *  Created on: 12/08/2013
 *      Author: ywangd
 */
#include "opcode.h"
#include "compiler.h"
#include "opcode.i"

Compiled *
newcompiled() {

    Compiled *com = (Compiled *) malloc(sizeof(Compiled));
    if (com == NULL) {
        return log_error(MEMORY_ERROR,
                "not enough memory to create new compiled");
    }

    if ((com->code = (unsigned char *) malloc(sizeof(unsigned char))) == NULL) {
        DEL(com);
        return log_error(MEMORY_ERROR, "not enough memory for code of compiled");
    }

    if ((com->consts = newlistobject(0)) == NULL) {
        DEL(com->code);
        DEL(com);
        return log_error(MEMORY_ERROR,
                "not enough memory for consts of compiled");
    }

    if ((com->names = newlistobject(0)) == NULL) {
        DEL(com->consts);
        DEL(com->code);
        DEL(com);
        return log_error(MEMORY_ERROR,
                "not enough memory for names of compiled");
    }

    com->nexti = 0;
    com->len = 1;
    return com;
}

void
printcompiled(Compiled *com) {
    int ii;
    int opcode;
    while (ii<com->len) {
        opcode = GET_OPCODE(com, ii);
        if (HAS_ARG(opcode)) {
            GET_ARG(com, ii)
        }
    }
}


static int
c_resize_code(Compiled *com) {
    com->code =
            (unsigned char *) realloc(com->code,
                    (com->len + 1000) * sizeof(unsigned char));
    if (com->code == NULL) {
        log_error(MEMORY_ERROR, "no memory to increase code length");
        return 0;
    }
    com->len += 1000;
    return 1;
}

static void
c_addbyte(Compiled *com, int byte) {
    if (byte < 0 || byte > 255) {
        fatal("trying to add invalid byte to code");
    }
    if (com->nexti >= com->len) {
        c_resize_code(com);
    }
    com->code[com->nexti++] = byte;
}

static void
c_addint(Compiled *com, int i) {
    if (i < 0) {
        fatal("trying to add invalid int to code");
    }
    c_addbyte(com, i & 0xff);
    c_addbyte(com, i >> 8);
}

static void
compile_assign(Compiled *com, AstNode *sn) {

    int idx;
    EmObject *ob;

    switch (sn->type) {
    case AST_IDENT:
        ob = newstringobject(AST_GET_LEXEME_SAFE(sn));
        idx = listobject_index(com->names, ob);
        if (idx < 0) {
            listobject_append(com->names, ob);
            idx = listobject_len(com->names) - 1;
        }
        c_addbyte(com, OP_POP);
        c_addint(com, idx);
        break;
    default:
        break;
    }
}

static void
compile_ast_node(Compiled *com, AstNode *sn) {

    int idx;
    EmObject *ob;

    switch (sn->type) {
    case AST_ASSIGN:
        compile_ast_node(com, AST_GET_MEMBER(sn,1));
        compile_assign(com, AST_GET_MEMBER(sn,0));
        break;

    case AST_LITERAL:
        ob = newstringobject(AST_GET_LEXEME_SAFE(sn));
        idx = listobject_index(com->consts, ob);
        if (idx < 0) {
            listobject_append(com->consts, ob);
            idx = listobject_len(com->consts) - 1;
        }
        c_addbyte(com, OP_PUSHC);
        c_addint(com, idx);
        DECREF(ob);
        break;

    default:
        break;
    }

}

Compiled *
compile_ast(AstNode *stree) {
    Compiled *com = newcompiled();

    int ii;
    for (ii = 0; ii < stree->size; ii++) {
        compile_ast_node(com, AST_GET_MEMBER(stree,ii));
    }

    return com;
}
