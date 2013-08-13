/*
 * compiler.c
 *
 *  Created on: 12/08/2013
 *      Author: ywangd
 */
#include "Emma.h"
#include "opcode.i"

#define DEFAULT_BLOCK_SIZE      16

#define GET_INSTR_FROM_BLOCK(b,i)       (&(b)->instrlist[i])
#define I_STR(instr)    opcode_types[instr->opcode]
#define I_HASARG(instr) instr->hasarg
#define I_ARG(instr)    instr->v.arg
#define I_TARGET(instr)    instr->v.target

#define SET_I_ARG(instr,a)    instr->v.arg = a
#define SET_I_TARGET(instr,t)   instr->v.target = t
#define SET_I_ROWCOL(instr,sn)  instr->row=sn->row; \
                                    instr->col=sn->col


#define NEXT_INSTR(b,i)   i=next_instr_from_block(b); \
                            if (i<0) longjmp(__compile_buf, 1); \


#define BINOP_OF_ASTTYPE(t)     t==AST_ADD ? OP_ADD : \
                                    (t==AST_SUB ? OP_SUB : \
                                    (t==AST_AND ? OP_AND : \
                                    (t==AST_OR ? OP_OR : \
                                    (t==AST_XOR ? OP_XOR : \
                                    (t==AST_GT ? OP_GT : \
                                    (t==AST_LT ? OP_LT : \
                                    (t==AST_GE ? OP_GE : \
                                    (t==AST_LE ? OP_LE : \
                                    (t==AST_EQ ? OP_EQ : \
                                    (t==AST_NE ? OP_NE : \
                                    (t==AST_MUL ? OP_MUL : \
                                    (t==AST_DIV ? OP_DIV : \
                                    (t==AST_MOD ? OP_MOD : OP_POW )))))))))))))

#define UNARYOP_OF_ASTTYPE(t)   t==AST_PLUS ? OP_PLUS : \
                                    (t==AST_MINUS ? OP_MINUS : OP_NOT)




static Compiler compiler;
static jmp_buf __compile_buf;

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
next_instr_from_block(Basicblock *b) {
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
    DEL(b)
    ;
}

void
freecompiledunit(CompiledUnit *cu) {
    if (cu->block)
        freebasicblock(cu->block);
    cu->block = cu->curblock = NULL;
    freeobj(cu->consts);
    freeobj(cu->names);
    DEL(cu)
    ;
}

void printcompiledunit(CompiledUnit *cu) {
    int ii;
    int opcode;
    Basicblock *b;
    Instr *instr;
    EmObject *ob;
    for (b = cu->block; b != NULL; b = b->next) {
        for (ii = 0; ii < b->inxt; ii++) {
            instr = GET_INSTR_FROM_BLOCK(b,ii);
            printf("%-20s",
                    I_STR(instr));
            if (instr->hasarg) {
                if (instr->isjump) {
                    printf("0x%08x", I_TARGET(instr));
                } else {
                    printf("%d ", instr->v.arg);
                    if (instr->opcode == OP_PUSHC) {
                        ob = listobject_get(cu->consts, I_ARG(instr));
                        printf("(%s)", tostrobj(ob));
                        DECREF(ob);

                    } else if (instr->opcode == OP_PUSH
                            || instr->opcode == OP_POP) {
                        ob = listobject_get(cu->names, I_ARG(instr));
                        printf("(%s)", tostrobj(ob));
                        DECREF(ob);
                    }
                }
            }
            printf("\n");
        }
        printf("\n");
    }

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
        NEXT_INSTR(cu->curblock, off);
        instr = GET_INSTR_FROM_BLOCK(cu->curblock,off);
        instr->opcode = OP_POP;
        instr->hasarg = 1;
        SET_I_ARG(instr, idx);
        SET_I_ROWCOL(instr, sn);
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
        NEXT_INSTR(cu->curblock, off);
        instr = GET_INSTR_FROM_BLOCK(cu->curblock,off);
        instr->opcode = OP_PUSHC;
        instr->hasarg = 1;
        SET_I_ARG(instr, idx);
        SET_I_ROWCOL(instr, sn);
        DECREF(ob);
        break;


    /*
     * Binary operators
     */
    case AST_ADD:
    case AST_SUB:
    case AST_AND:
    case AST_OR:
    case AST_XOR:
    case AST_GT:
    case AST_LT:
    case AST_GE:
    case AST_LE:
    case AST_EQ:
    case AST_NE:
    case AST_MUL:
    case AST_DIV:
    case AST_MOD:
    case AST_POW:
        compile_ast_node(AST_GET_MEMBER(sn,0));
        compile_ast_node(AST_GET_MEMBER(sn,1));
        NEXT_INSTR(cu->curblock, off);
        instr = GET_INSTR_FROM_BLOCK(cu->curblock,off);
        instr->opcode = BINOP_OF_ASTTYPE(sn->type);
        break;

    /*
     * Unary operators
     */
    case AST_PLUS:
    case AST_MINUS:
    case AST_NOT:
        compile_ast_node(AST_GET_MEMBER(sn,0));
        NEXT_INSTR(cu->curblock, off);
        instr = GET_INSTR_FROM_BLOCK(cu->curblock,off);
        instr->opcode = UNARYOP_OF_ASTTYPE(sn->type);
        break;

    default:
        break;
    }

}

static int
compiler_init() {
    compiler.cu = newcompiledunit();
    return 1;
}

CompiledUnit *
compile_ast(AstNode *stree) {
    int ii;
    compiler_init();

    if (setjmp(__compile_buf) == 0) {
        for (ii = 0; ii < stree->size; ii++) {
            compile_ast_node(AST_GET_MEMBER(stree,ii));
        }
    } else {
        freecompiledunit(compiler.cu);
        compiler.cu = NULL;
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
