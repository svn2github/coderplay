/*
 * compiler.c
 *
 *  Created on: 12/08/2013
 *      Author: ywangd
 */
#include "Emma.h"
#include "opcode.i"

#define DEFAULT_BLOCK_SIZE      16

#define INSTR_AT(b,i)       (&(b)->instrlist[i])
#define I_STR(instr)        opcode_types[instr->opcode]
#define I_HASARG(instr)     (instr)->opcode>OP_HASARG?1:0
#define I_ISJUMP(instr)     ((instr)->opcode==OP_JUMP || \
                                (instr)->opcode == OP_FJUMP || \
                                (instr)->opcode == OP_FOR) ? 1 : 0
#define I_ARG(instr)        instr->v.arg
#define I_TARGET(instr)     instr->v.target

#define SET_I_ARG(instr,a)    instr->v.arg = a
#define SET_I_TARGET(instr,t)   instr->v.target = t
#define SET_I_ROWCOL(instr,sn)  instr->row=sn->row; \
                                    instr->col=sn->col

#define SET_NEW_BLOCK(cu,b)     (cu)->curblock->next = b; \
                                    (cu)->curblock = b

#define PUSH_CONTINUE_BLOCK(cu,b)   (cu)->continueblock[cu->i_continueblock++] = b; \
                                        if (cu->i_continueblock >= MAX_NEST_LEVEL) { \
                                            log_error(MEMORY_ERROR, "continue block overflow"); \
                                            longjmp(__compile_buf, 1); \
                                        }

#define PUSH_BREAK_BLOCK(cu,b)      (cu)->breakblock[cu->i_breakblock++] = b; \
                                        if (cu->i_breakblock >= MAX_NEST_LEVEL) { \
                                            log_error(MEMORY_ERROR, "break block overflow"); \
                                            longjmp(__compile_buf, 1); \
                                        }

#define POP_CONTINUE_BLOCK(cu)      (cu)->i_continueblock--; \
                                        if (cu->i_continueblock < 0) { \
                                            log_error(MEMORY_ERROR, "continue block underflow"); \
                                            longjmp(__compile_buf, 1); \
                                        }

#define POP_BREAK_BLOCK(cu)         (cu)->i_breakblock--; \
                                        if (cu->i_breakblock < 0) { \
                                            log_error(MEMORY_ERROR, "break block underflow"); \
                                            longjmp(__compile_buf, 1); \
                                        }

#define GET_CONTINUE_BLOCK(cu)      (cu)->continueblock[cu->i_continueblock-1]
#define GET_BREAK_BLOCK(cu)         (cu)->breakblock[cu->i_breakblock-1]

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
    b->lineno = 0;
    b->next = NULL;
    b->instrlist = NULL;
    b->inxt = 0;
    b->ilen = 0;
    return b;
}

static Instr*
next_instr(Basicblock *b) {
    if (b->instrlist == NULL) {
        b->instrlist = newinstr(DEFAULT_BLOCK_SIZE);
        if (b->instrlist == NULL) {
            log_error(MEMORY_ERROR, "can get no more instruction");
            longjmp(__compile_buf, 1);
        }
        b->inxt = 0;
        b->ilen = DEFAULT_BLOCK_SIZE;
    } else if (b->inxt == b->ilen) {
        size_t oldsize, newsize;
        oldsize = b->ilen * sizeof(Instr);
        newsize = oldsize << 1;
        b->instrlist = (Instr *) realloc(b->instrlist, newsize);
        if (b->instrlist == NULL) {
            log_error(MEMORY_ERROR, "can get no more instruction");
            longjmp(__compile_buf, 1);
        }
        memset((char *) b->instrlist + oldsize, 0, newsize - oldsize);
        b->ilen <<= 1;
    }
    return INSTR_AT(b, b->inxt++);
}
static void freebasicblock(Basicblock *b);

static CompiledUnit *
newcompiledunit() {

    CompiledUnit *cu = (CompiledUnit *) malloc(sizeof(CompiledUnit));
    if (cu == NULL) {
        return log_error(MEMORY_ERROR,
                "not enough memory to create new compiled unit");
    }

    if ((cu->block = newbasicblock()) == NULL) {
        DEL(cu);
        return NULL;;
    }
    cu->curblock = cu->block;

    if ((cu->consts = newlistobject(0)) == NULL) {
        freebasicblock(cu->block);
        DEL(cu);
        return log_error(MEMORY_ERROR,
                "not enough memory for consts of compiled unit");
    }

    if ((cu->names = newlistobject(0)) == NULL) {
        freeobj(cu->consts);
        freebasicblock(cu->block);
        DEL(cu);
        return log_error(MEMORY_ERROR,
                "not enough memory for names of compiled unit");
    }

    cu->continueblock = (Basicblock **) malloc(
            sizeof(Basicblock *) * MAX_NEST_LEVEL);
    cu->breakblock = (Basicblock **) malloc(
            sizeof(Basicblock *) * MAX_NEST_LEVEL);

    if (cu->continueblock == NULL || cu->breakblock == NULL) {
        DEL(cu->continueblock);
        DEL(cu->breakblock);
        freeobj(cu->consts);
        freebasicblock(cu->block);
        DEL(cu);
        return log_error(MEMORY_ERROR,
                "no memory for continue and break block management");
    }

    cu->i_continueblock = cu->i_breakblock = 0;

    return cu;
}

static void freebasicblock(Basicblock *b) {
    if (b->next)
        freebasicblock(b->next);
    DEL(b->instrlist);
    DEL(b)
    ;
}

void freecompiledunit(CompiledUnit *cu) {
    if (cu->block)
        freebasicblock(cu->block);
    cu->block = cu->curblock = NULL;
    freeobj(cu->consts);
    freeobj(cu->names);
    DEL(cu->continueblock);
    DEL(cu->breakblock);
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
        printf("block at <0x%08x>\n", b);
        for (ii = 0; ii < b->inxt; ii++) {
            instr = INSTR_AT(b,ii);
            printf("%-20s",
            I_STR(instr));
            if (I_HASARG(instr)) {
                if (I_ISJUMP(instr)) {
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

static void compile_ast_node(AstNode *sn);
static void compile_assign(AstNode *sn);
static void compile_identifier(AstNode *sn, int opcode);

static void compile_if(AstNode *sn) {
    CompiledUnit *cu = compiler.cu;
    Instr *instr;
    Basicblock *elseblock, *endblock;

    compile_ast_node(AST_GET_MEMBER(sn,0)); // test
    elseblock = newbasicblock();
    instr = next_instr(cu->curblock);
    instr->opcode = OP_FJUMP;
    SET_I_TARGET(instr, elseblock);
    compile_ast_node(AST_GET_MEMBER(sn,1));
    if (AST_GET_MEMBER(sn,2)->size > 0) { // non-empty else clause
        endblock = newbasicblock();
        instr = next_instr(cu->curblock);
        instr->opcode = OP_JUMP;
        SET_I_TARGET(instr, endblock);
        cu->curblock->next = elseblock;
        cu->curblock = elseblock;
        compile_ast_node(AST_GET_MEMBER(sn,2));
    } else { // empty else clause
        endblock = elseblock;
    }
    cu->curblock->next = endblock;
    cu->curblock = endblock;
}

static void compile_while(AstNode *sn) {
    CompiledUnit *cu = compiler.cu;
    Instr *instr;
    Basicblock *whileblock, *endblock;

    // The marking blocks
    whileblock = newbasicblock();
    endblock = newbasicblock();

    // Start new block for while
    SET_NEW_BLOCK(cu, whileblock);
    // test
    compile_ast_node(AST_GET_MEMBER(sn,0));
    instr = next_instr(cu->curblock);
    instr->opcode = OP_FJUMP;
    SET_I_TARGET(instr, endblock);

    // manage possible break or continue
    PUSH_CONTINUE_BLOCK(cu, whileblock);
    PUSH_BREAK_BLOCK(cu, endblock);

    // while body
    compile_ast_node(AST_GET_MEMBER(sn,1));

    // manage possible break or continue
    POP_CONTINUE_BLOCK(cu);
    POP_BREAK_BLOCK(cu);

    // loop to the start
    instr = next_instr(cu->curblock);
    instr->opcode = OP_JUMP;
    SET_I_TARGET(instr, whileblock);

    // Start new block after while
    SET_NEW_BLOCK(cu, endblock);

}

static void compile_for(AstNode *sn) {
    CompiledUnit *cu = compiler.cu;
    Instr *instr;
    Basicblock *forblock, *endblock;

    // The marking blocks
    forblock = newbasicblock();
    endblock = newbasicblock();

    // The loop variables: start, end, step
    compile_ast_node(AST_GET_MEMBER(sn,1));
    instr = next_instr(cu->curblock);
    // change stack order to step, end, start
    instr->opcode = OP_ROT_THREE;
    // Assign start to counter
    compile_assign(AST_GET_MEMBER(sn,0));
    // Setup the for loop, including pre-decrease counter
    instr = next_instr(cu->curblock);
    instr->opcode = OP_SETUP_FOR;

    /*
     * Now the for block
     */
    // new block for the forloop
    SET_NEW_BLOCK(cu, forblock);
    /*
     * The FOR instruction increase the counter and test for
     * the end. Then push them back for next loop iteration.
     */
    instr->opcode = OP_FOR;
    SET_I_TARGET(instr, endblock);

    // manage possible break or continue
    PUSH_CONTINUE_BLOCK(cu, forblock);
    PUSH_BREAK_BLOCK(cu, endblock);

    // The loop body
    compile_ast_node(AST_GET_MEMBER(sn,2));

    // manage possible break or continue
    POP_CONTINUE_BLOCK(cu);
    POP_BREAK_BLOCK(cu);

    // loop to the start
    instr = next_instr(cu->curblock);
    instr->opcode = OP_JUMP;
    SET_I_TARGET(instr, forblock);

    // End of the for loop
    SET_NEW_BLOCK(cu, endblock);
}

static void compile_arglist(AstNode *sn) {
    int ii, idx, count;
    EmObject *ob;
    CompiledUnit *cu = compiler.cu;
    Instr *instr;
    if (sn->size == 0) { // empty list
        ob = hashobject_lookup_by_string(literalTable, "null");
        idx = listobject_index(cu->consts, ob);
        if (idx < 0) {
            cu->consts = listobject_append(cu->consts, ob);
            idx = listobject_len(cu->consts) - 1;
        }
        DECREF(ob);
        instr = next_instr(cu->curblock);
        instr->opcode = OP_PUSHC;
        SET_I_ARG(instr, idx);
        SET_I_ROWCOL(instr, sn)
        ;
    } else { // non-empty list
        /*
         * Regular positional parameter first
         */
        count = 0;
        for (ii = 0; ii < sn->size; ii++) {
            if (AST_GET_MEMBER(sn,ii)->type != AST_KVPAIR) {
                compile_ast_node(AST_GET_MEMBER(sn,ii));
                count++;
            }
        }
        /*
         * Process any keyword style params
         */
        if (count != sn->size) { // still have keyword args
            for (ii = 0; ii < sn->size; ii++) {
                if (AST_GET_MEMBER(sn,ii)->type == AST_KVPAIR) {
                    compile_ast_node(AST_GET_MEMBER(sn,ii));
                }
            }
            instr = next_instr(cu->curblock);
            instr->opcode = OP_MKHASH;
            SET_I_ARG(instr, count);
            SET_I_ROWCOL(instr, sn);
            count++; // hash is only 1 more element for the list
        }
        instr = next_instr(cu->curblock);
        instr->opcode = OP_MKLIST;
        SET_I_ARG(instr, count);
        SET_I_ROWCOL(instr, sn)
        ;
    }
}

static void compile_identifier(AstNode *sn, int opcode) {
    int idx;
    EmObject *ob;
    CompiledUnit *cu = compiler.cu;
    Instr *instr;

    ob = newstringobject(AST_GET_LEXEME_SAFE(sn));
    idx = listobject_index(cu->names, ob);
    if (idx < 0) {
        cu->names = listobject_append(cu->names, ob);
        idx = listobject_len(cu->names) - 1;
    }
    DECREF(ob);
    instr = next_instr(cu->curblock);
    instr->opcode = opcode;
    SET_I_ARG(instr, idx);
    SET_I_ROWCOL(instr, sn);
}

static void compile_assign(AstNode *sn) {

    int idx;
    EmObject *ob;
    CompiledUnit *cu = compiler.cu;
    Instr *instr;

    switch (sn->type) {
    case AST_IDENT:
        compile_identifier(sn, OP_POP);
        break;

    case AST_FIELD:
        compile_ast_node(AST_GET_MEMBER(sn,1)); // field
        compile_ast_node(AST_GET_MEMBER(sn,0));
        instr = next_instr(cu->curblock);
        instr->opcode = OP_SET_FIELD;
        break;

    case AST_INDEX:
        compile_ast_node(AST_GET_MEMBER(sn,1)); // index
        compile_ast_node(AST_GET_MEMBER(sn,0));
        instr = next_instr(cu->curblock);
        instr->opcode = OP_SET_INDEX;
        break;

    default:
        break;
    }
}

static void compile_ast_node(AstNode *sn) {

    int ii, idx, count;
    EmObject *ob;
    CompiledUnit *cu = compiler.cu;
    Instr *instr;

    switch (sn->type) {
    case AST_SEQ:
        for (ii = 0; ii < sn->size; ii++) {
            compile_ast_node(AST_GET_MEMBER(sn,ii));
        }
        break;

    case AST_ASSIGN:
        compile_ast_node(AST_GET_MEMBER(sn,1));
        compile_assign(AST_GET_MEMBER(sn,0));
        break;

    case AST_IDENT:
        compile_identifier(sn, OP_PUSH);
        break;

    case AST_CALL:
        compile_ast_node(AST_GET_MEMBER(sn,0)); // the func
        compile_arglist(AST_GET_MEMBER(sn,1)); // the parameter
        instr = next_instr(cu->curblock);
        instr->opcode = OP_CALL;
        SET_I_ROWCOL(instr, sn)
        ;
        break;

    case AST_LITERAL:
        ob = hashobject_lookup_by_string(literalTable, AST_GET_LEXEME_SAFE(sn));
        idx = listobject_index(cu->consts, ob);
        if (idx < 0) {
            cu->consts = listobject_append(cu->consts, ob);
            idx = listobject_len(cu->consts) - 1;
        }
        DECREF(ob);
        instr = next_instr(cu->curblock);
        instr->opcode = OP_PUSHC;
        SET_I_ARG(instr, idx);
        SET_I_ROWCOL(instr, sn)
        ;
        break;

    case AST_LIST:
        for (ii = 0; sn->size; ii++) {
            compile_ast_node(AST_GET_MEMBER(sn,ii));
        }
        break;

    case AST_KVPAIR:
        compile_ast_node(AST_GET_MEMBER(sn,0));
        compile_ast_node(AST_GET_MEMBER(sn,1));
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
        instr = next_instr(cu->curblock);
        instr->opcode = BINOP_OF_ASTTYPE(sn->type);
        break;

        /*
         * Unary operators
         */
    case AST_PLUS:
    case AST_MINUS:
    case AST_NOT:
        compile_ast_node(AST_GET_MEMBER(sn,0));
        instr = next_instr(cu->curblock);
        instr->opcode = UNARYOP_OF_ASTTYPE(sn->type);
        break;

    case AST_IF:
        compile_if(sn);
        break;

    case AST_WHILE:
        compile_while(sn);
        break;

    case AST_FOR:
        compile_for(sn);
        break;

    case AST_CONTINUE:
        instr = next_instr(cu->curblock);
        instr->opcode = OP_JUMP;
        SET_I_TARGET(instr, GET_CONTINUE_BLOCK(cu));
        break;

    case AST_BREAK:
        instr = next_instr(cu->curblock);
        instr->opcode = OP_JUMP;
        SET_I_TARGET(instr, GET_BREAK_BLOCK(cu));
        break;

    default:
        break;
    }

}

static int compiler_init() {
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
        fatal("compiler error");
        fprintf(stderr, "ERROR compile\n");
        freecompiledunit(compiler.cu);
        compiler.cu = NULL;
    }

    return compiler.cu;
}

