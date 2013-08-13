/*
 * compiler.c
 *
 *  Created on: 12/08/2013
 *      Author: ywangd
 */
#include "Emma.h"
#include "opcode.i"

static Compiler compiler;

static Instr *
newinstr(int size) {
    Instr * i = (Instr *) malloc(sizeof(Instr) * size);
    if (i == NULL) {
        return log_error(MEMORY_ERROR, "no memory for new instruction");
    }
    memset((char *) i, 0, sizeof(Instr) * size); // initialize to zeros
    return i;
}

static Basicblock *
newbasicblock() {
    Basicblock *b = (Basicblock *) malloc(sizeof(Basicblock));
    if (b == NULL) {
        return log_error(MEMORY_ERROR, "no memory for new basic block");
    }
    b->next = NULL;
    b->instrlist = NULL;
    b->inxt = 0;
    b->ilen = 0;
    return b;
}

static int
get_next_instr_from_block(Basicblock *b) {
    if (b->instrlist == NULL) {
        b->instrlist = newinstr(DEFAULT_BLOCK_SIZE);
        if (b->instrlist == NULL) {
            return -1;
        }
        b->inxt = 0;
        b->ilen = DEFAULT_BLOCK_SIZE;
    } else if (b->inxt == b->ilen) {
        size_t oldsize, newsize;
        oldsize = b->ilen * sizeof(Instr);
        newsize = oldsize << 1;
        b->instrlist = (Instr *) realloc(b->instrlist, newsize);
        if (b->instrlist == NULL) {
            return -1;
        }
        memset((char *) b->instrlist + oldsize, 0, newsize - oldsize);
    }
    return b->inxt++;
}

static CompiledUnit *
newcompiledunit() {

    CompiledUnit *c = (CompiledUnit *) malloc(sizeof(CompiledUnit));
    if (c == NULL) {
        return log_error(MEMORY_ERROR,
                "not enough memory to create new compiled unit");
    }

    if ((c->block = newbasicblock()) == NULL) {
        DEL(c);
        return NULL;;
    }
    c->curblock = c->block;

    if ((c->consts = newlistobject(0)) == NULL) {
        DEL(c->block);
        DEL(c);
        return log_error(MEMORY_ERROR,
                "not enough memory for consts of compiled unit");
    }

    if ((c->names = newlistobject(0)) == NULL) {
        DEL(c->block);
        DEL(c->consts);
        DEL(c);
        return log_error(MEMORY_ERROR,
                "not enough memory for names of compiled unit");
    }

    return c;
}


static void
freebasicblock(Basicblock *b) {
    if (b->next)
        freebasicblock(b->next);
    DEL(b->instrlist);
    DEL(b);
}

void
freecompiledunit(CompiledUnit *cu) {
    if (cu->block)
        freebasicblock(cu->block);
    cu->block = cu->curblock = NULL;
    freeobj(cu->consts);
    freeobj(cu->names);
}


void printcompiled(CompiledUnit *cu) {
    int ii;
    int opcode;

}


static void compile_assign(AstNode *sn) {

    int idx, off;
    EmObject *ob;
    CompiledUnit *cu = compiler.cu;
    Instr *instr;

    switch (sn->type) {
    case AST_IDENT:
        ob = newstringobject(AST_GET_LEXEME_SAFE(sn));
        idx = listobject_index(cu->names, ob);
        if (idx < 0) {
            listobject_append(cu->names, ob);
            idx = listobject_len(cu->names) - 1;
        }
        off = get_next_instr_from_block(cu->curblock);
        instr = GET_INSTR_FROM_BLOCK(cu->curblock,off);
        instr->opcode = OP_POP;
        instr->hasarg = 1;
        instr->v.arg = idx;
        instr->row = sn->row;
        instr->col = sn->col;
        DECREF(ob);
        break;
    default:
        break;
    }
}

static void compile_ast_node(AstNode *sn) {

    int idx, off;
    EmObject *ob;
    CompiledUnit *cu = compiler.cu;
    Instr *instr;

    switch (sn->type) {
    case AST_ASSIGN:
        compile_ast_node(AST_GET_MEMBER(sn,1));
        compile_assign(AST_GET_MEMBER(sn,0));
        break;

    case AST_LITERAL:
        ob = hashobject_lookup_by_string(literalTable, AST_GET_LEXEME_SAFE(sn));
        idx = listobject_index(cu->consts, ob);
        if (idx < 0) {
            listobject_append(cu->consts, ob);
            idx = listobject_len(cu->consts) - 1;
        }
        off = get_next_instr_from_block(cu->curblock);
        instr = GET_INSTR_FROM_BLOCK(cu->curblock,off);
        instr->opcode = OP_PUSHC;
        instr->hasarg = 1;
        instr->v.arg = idx;
        instr->row = sn->row;
        instr->col = sn->col;
        DECREF(ob);
        break;

    default:
        break;
    }

}

CompiledUnit *
compile_ast(AstNode *stree) {

    compiler.cu = newcompiledunit();

    int ii;
    for (ii = 0; ii < stree->size; ii++) {
        compile_ast_node(AST_GET_MEMBER(stree,ii));
    }
    return compiler.cu;
}










//static int
//c_resize_code(CompiledUnit *c) {
//    c->code =
//            (unsigned char *) realloc(c->code,
//                    (c->len + 1000) * sizeof(unsigned char));
//    if (c->code == NULL) {
//        log_error(MEMORY_ERROR, "no memory to increase code length");
//        return 0;
//    }
//    c->len += 1000;
//    return 1;
//}

//static void
//c_addbyte(CompiledUnit *c, int byte) {
//    if (byte < 0 || byte > 255) {
//        fatal("trying to add invalid byte to code");
//    }
//    if (c->nexti >= c->len) {
//        c_resize_code(c);
//    }
//    c->code[c->nexti++] = byte;
//}
//
//static void
//c_addint(CompiledUnit *c, int i) {
//    if (i < 0) {
//        fatal("trying to add invalid int to code");
//    }
//    c_addbyte(c, i & 0xff);
//    c_addbyte(c, i >> 8);
//}
