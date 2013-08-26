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
                                (instr)->opcode == OP_TJUMP || \
                                (instr)->opcode == OP_FOR) ? 1 : 0
#define I_ARG(instr)        instr->v.arg
#define I_TARGET(instr)     instr->v.target

#define SET_I_ARG(instr,a)    instr->v.arg = a
#define SET_I_TARGET(instr,t)   instr->v.target = t

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
                                    (t==AST_XOR ? OP_XOR : \
                                    (t==AST_GT ? OP_GT : \
                                    (t==AST_LT ? OP_LT : \
                                    (t==AST_GE ? OP_GE : \
                                    (t==AST_LE ? OP_LE : \
                                    (t==AST_EQ ? OP_EQ : \
                                    (t==AST_NE ? OP_NE : \
                                    (t==AST_MUL ? OP_MUL : \
                                    (t==AST_DIV ? OP_DIV : \
                                    (t==AST_MOD ? OP_MOD : OP_POW )))))))))))

#define UNARYOP_OF_ASTTYPE(t)   t==AST_PLUS ? OP_PLUS : \
                                    (t==AST_MINUS ? OP_MINUS : OP_NOT)

static Compiler compiler;
static jmp_buf __compile_buf;
static int cur_row;

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

static EmCodeObject *compile_ast_unit(AstNode *sn, int saveEnv);
static void compile_ast_node(AstNode *sn);
static void compile_assign(AstNode *sn);
static void compile_identifier(AstNode *sn, int opcode);

static int idx_in_consts(char *key) {
    EmObject *ob, *keyob;
    CompiledUnit *cu = compiler.cu;
    int idx;

    keyob = newstringobject(key);
    if (hashobject_haskey(compiler.symtab, keyob)) {
        ob = hashobject_lookup(compiler.symtab, keyob);
        idx = ((EmIntObject *) ob)->ival;
        DECREF(ob);
    } else {
        ob = hashobject_lookup(literalTable, keyob);
        listobject_append(cu->consts, ob);
        DECREF(ob);
        idx = listobject_len(cu->consts) - 1;
        ob = newintobject(idx);
        hashobject_insert(compiler.symtab, keyob, ob);
        DECREF(ob);
    }
    DECREF(keyob);
    return idx;
}

static int idx_in_names(char *name) {
    EmObject *ob, *nameob;
    CompiledUnit *cu = compiler.cu;
    int idx;

    nameob = newstringobject(name);
    if (hashobject_haskey(compiler.symtab, nameob)) {
        ob = hashobject_lookup(compiler.symtab, nameob);
        idx = ((EmIntObject *) ob)->ival;
        DECREF(ob);
    } else {
        listobject_append(cu->names, nameob);
        idx = listobject_len(cu->names) - 1;
        ob = newintobject(idx);
        hashobject_insert(compiler.symtab, nameob, ob);
        DECREF(ob);
    }
    DECREF(nameob);
    return idx;
}


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
        // start new block for else
        SET_NEW_BLOCK(cu, elseblock);
        compile_ast_node(AST_GET_MEMBER(sn,2));
    } else { // empty else clause
        endblock = elseblock;
    }
    // start new block for things after the if-else
    SET_NEW_BLOCK(cu, endblock);
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
        idx = idx_in_consts("null");
        instr = next_instr(cu->curblock);
        instr->opcode = OP_PUSHC;
        SET_I_ARG(instr, idx);

    } else { // non-empty list
        /*
         * Regular positional arguments first
         */
        count = 0;
        for (ii = 0; ii < sn->size; ii++) {
            if (AST_GET_MEMBER(sn,ii)->type != AST_KVPAIR) {
                compile_ast_node(AST_GET_MEMBER(sn,ii));
                count++;
            }
        }
        if (count > 0) {
            instr = next_instr(cu->curblock);
            instr->opcode = OP_MKLIST;
            SET_I_ARG(instr, count);
        } else {
            idx = idx_in_consts("null");
            instr = next_instr(cu->curblock);
            instr->opcode = OP_PUSHC;
            SET_I_ARG(instr, idx);
        }

        /*
         * Process any keyword style arguments
         */
        if (count != sn->size) { // still have keyword args
            count = 0;
            for (ii = 0; ii < sn->size; ii++) {
                if (AST_GET_MEMBER(sn,ii)->type == AST_KVPAIR) {
                    compile_ast_node(AST_GET_MEMBER(sn,ii));
                    count++;
                }
            }
            instr = next_instr(cu->curblock);
            instr->opcode = OP_MKHASH;
            SET_I_ARG(instr, count);
        } else {
            idx = idx_in_consts("null");
            instr = next_instr(cu->curblock);
            instr->opcode = OP_PUSHC;
            SET_I_ARG(instr, idx);
        }

        // make a single list for both position and keyword args
        instr = next_instr(cu->curblock);
        instr->opcode = OP_MKLIST;
        SET_I_ARG(instr, 2);
    }
}

static void compile_regular_params(AstNode *sn) {
    int ii, idx, count;
    EmObject *ob;
    CompiledUnit *cu = compiler.cu;
    Instr *instr;
    AstNode *sn_temp;

    if (sn->size == 0) { // no regular parameters
        instr = next_instr(cu->curblock);
        instr->opcode = OP_REFUSE_POSARGS;

    } else {
        /*
         * Process any keyword params first
         */
        count = 0;
        for (ii = 0; ii < sn->size; ii++) {
            if (AST_GET_MEMBER(sn,ii)->type == AST_KVPAIR) {
                sn_temp = AST_GET_MEMBER(sn,ii);
                compile_ast_node(AST_GET_MEMBER(sn_temp,1));
                compile_identifier(AST_GET_MEMBER(sn_temp,0),OP_POP);
                count++;
            }
        }
        if (count > 0) {
            instr = next_instr(cu->curblock);
            instr->opcode = OP_GET_KWARGS;
        } else {
            instr = next_instr(cu->curblock);
            instr->opcode = OP_REFUSE_KWARGS;
        }

        /*
         * Regular positional parameters if any
         */
        if (count != sn->size) { // still have positional parameters
            count = 0;
            for (ii = 0; ii < sn->size; ii++) {
                if (AST_GET_MEMBER(sn,ii)->type != AST_KVPAIR) {
                    compile_identifier(AST_GET_MEMBER(sn,ii), OP_PUSHN);
                    count++;
                }
            }
            instr = next_instr(cu->curblock);
            instr->opcode = OP_MKLIST;
            SET_I_ARG(instr, count);
            instr = next_instr(cu->curblock);
            instr->opcode = OP_GET_POSARGS;
        } else {
            instr = next_instr(cu->curblock);
            instr->opcode = OP_REFUSE_POSARGS;
        }
    }
}

static void compile_paramlist(AstNode *sn) {
    int ii, idx, count;
    EmObject *ob;
    CompiledUnit *cu = compiler.cu;
    Instr *instr;
    AstNode *sn_sub;

    if (sn->size == 0) {
        // empty paramlist
        instr = next_instr(cu->curblock);
        instr->opcode = OP_REFUSE_POSARGS;
        instr = next_instr(cu->curblock);
        instr->opcode = OP_REFUSE_KWARGS;
        instr = next_instr(cu->curblock);
        instr->opcode = OP_NO_EXTRAP;
        instr = next_instr(cu->curblock);
        instr->opcode = OP_NO_EXTRAK;

    } else {

        // positional and keyword parameters
        compile_regular_params(AST_GET_MEMBER(sn,0));

        // extra p
        sn_sub = AST_GET_MEMBER(sn,1);
        if (sn_sub->size == 0) {
            instr = next_instr(cu->curblock);
            instr->opcode = OP_NO_EXTRAP;
        } else {
            idx = idx_in_names(AST_GET_LEXEME_SAFE(AST_GET_MEMBER(sn_sub,0)));
            instr = next_instr(cu->curblock);
            instr->opcode = OP_PUSHN;
            SET_I_ARG(instr, idx);
            instr = next_instr(cu->curblock);
            instr->opcode = OP_SET_EXTRAP;
        }

        // extra k;
        sn_sub = AST_GET_MEMBER(sn,2);
        if (sn_sub->size == 0) {
            instr = next_instr(cu->curblock);
            instr->opcode = OP_NO_EXTRAK;
        } else {
            idx = idx_in_names(AST_GET_LEXEME_SAFE(AST_GET_MEMBER(sn_sub,0)));
            instr = next_instr(cu->curblock);
            instr->opcode = OP_PUSHN;
            SET_I_ARG(instr, idx);
            instr = next_instr(cu->curblock);
            instr->opcode = OP_SET_EXTRAK;
        }
    }
}

static void compile_identifier(AstNode *sn, int opcode) {
    int idx;
    EmObject *ob;
    CompiledUnit *cu = compiler.cu;
    Instr *instr;

    idx = idx_in_names(AST_GET_LEXEME_SAFE(sn));
    instr = next_instr(cu->curblock);
    instr->opcode = opcode;
    SET_I_ARG(instr, idx);
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
        compile_ast_node(AST_GET_MEMBER(sn,0));
        compile_ast_node(AST_GET_MEMBER(sn,1)); // field
        instr = next_instr(cu->curblock);
        instr->opcode = OP_SET_FIELD;
        break;

    case AST_INDEX:
        compile_ast_node(AST_GET_MEMBER(sn,0));
        compile_ast_node(AST_GET_MEMBER(sn,1)); // index
        instr = next_instr(cu->curblock);
        instr->opcode = OP_SET_INDEX;
        break;

    case AST_SLICE:
        compile_ast_node(AST_GET_MEMBER(sn,0));
        compile_ast_node(AST_GET_MEMBER(sn,1)); // slice
        instr = next_instr(cu->curblock);
        instr->opcode = OP_MKLIST;
        SET_I_ARG(instr, 3);
        instr = next_instr(cu->curblock);
        instr->opcode = OP_SET_SLICE;
        break;

    case AST_IDXLIST:
        compile_ast_node(AST_GET_MEMBER(sn,0));
        compile_ast_node(AST_GET_MEMBER(sn,1)); // idxlist
        instr = next_instr(cu->curblock);
        instr->opcode = OP_MKLIST;
        SET_I_ARG(instr, AST_GET_MEMBER(sn,1)->size);
        instr = next_instr(cu->curblock);
        instr->opcode = OP_SET_IDXLIST;
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

    if (sn->row > cur_row) {
        instr = next_instr(cu->curblock);
        instr->opcode = OP_SET_ROW;
        SET_I_ARG(instr, sn->row);
        cur_row = sn->row;
    }

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
        break;

    case AST_LITERAL:
        idx = idx_in_consts(AST_GET_LEXEME_SAFE(sn));
        instr = next_instr(cu->curblock);
        instr->opcode = OP_PUSHC;
        SET_I_ARG(instr, idx);
        break;

    case AST_LIST:
        for (ii = 0; ii < sn->size; ii++) {
            compile_ast_node(AST_GET_MEMBER(sn,ii));
        }
        break;

    case AST_KVPAIR:
        compile_identifier(AST_GET_MEMBER(sn,0), OP_PUSHN);
        compile_ast_node(AST_GET_MEMBER(sn,1));
        break;

        /*
         * Binary operators
         */

    case AST_SUB:
    case AST_ADD:
    case AST_MUL:
    case AST_DIV:
    case AST_MOD:
    case AST_POW:
    case AST_XOR:
    case AST_GT:
    case AST_LT:
    case AST_GE:
    case AST_LE:
    case AST_EQ:
    case AST_NE:
        compile_ast_node(AST_GET_MEMBER(sn,0));
        compile_ast_node(AST_GET_MEMBER(sn,1));
        instr = next_instr(cu->curblock);
        instr->opcode = BINOP_OF_ASTTYPE(sn->type);
        break;

        /*
         * short-curcuit logic operators
         */
    case AST_AND:
    case AST_OR:
        compile_ast_node(AST_GET_MEMBER(sn,0));
        Basicblock *sc_block = newbasicblock();
        instr = next_instr(cu->curblock);
        if (sn->type == AST_AND)
            instr->opcode = OP_FJUMP;
        else
            instr->opcode = OP_TJUMP;
        SET_I_TARGET(instr, sc_block);
        compile_ast_node(AST_GET_MEMBER(sn,1));
        SET_NEW_BLOCK(cu, sc_block)
        ;
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

    case AST_PRINT:
        compile_ast_node(AST_GET_MEMBER(sn,0)); // the destination
        compile_ast_node(AST_GET_MEMBER(sn,1)); // the item list
        instr = next_instr(cu->curblock);
        instr->opcode = OP_MKLIST;
        SET_I_ARG(instr, AST_GET_MEMBER(sn,1)->size);
        instr = next_instr(cu->curblock);
        instr->opcode = OP_PRINT;
        break;

    case AST_READ:
        break;

    case AST_DEL:
        /*
         * Note the list has to be pushed by the variable names
         * instead of the contents.
         */
        for (ii=0; ii<sn->size; ii++) {
            compile_identifier(AST_GET_MEMBER(sn,ii), OP_PUSHN);
        }
        instr = next_instr(cu->curblock);
        instr->opcode = OP_MKLIST;
        SET_I_ARG(instr, sn->size);
        instr = next_instr(cu->curblock);
        instr->opcode = OP_DEL;
        break;

    case AST_FUNCDEF:

        // Create a new compiled unit for the function body
        compiler.cu = newcompiledunit();
        EmObject *symtab = compiler.symtab;
        compiler.symtab = newhashobject();

        // Compile parameters
        compile_paramlist(AST_GET_MEMBER(sn,1));

        // compile the body of function
        ob = (EmObject *) compile_ast_unit(AST_GET_MEMBER(sn,2),0);

        // restore to the parent compiled unit
        compiler.cu = cu;
        compiler.symtab = symtab;

        // Simply add the body code object to the end of the consts list.
        // This assumes no duplicate function definitions.
        // Although duplicate function defs are legal, it makes no sense
        // to have duplications. So I am not going to take care of duplications
        // here for code simplicity.
        listobject_append(cu->consts, ob);
        idx = listobject_len(cu->consts) - 1;
        DECREF(ob);
        instr = next_instr(cu->curblock);
        instr->opcode = OP_PUSHC;
        SET_I_ARG(instr, idx);

        // build the function
        instr = next_instr(cu->curblock);
        instr->opcode = OP_FUNCDEF;

        // store it to a variable name
        compile_identifier(AST_GET_MEMBER(sn,0), OP_POP);
        break;

    case AST_RETURN:
        compile_ast_node(AST_GET_MEMBER(sn,0));
        instr = next_instr(cu->curblock);
        instr->opcode = OP_RETURN;
        break;

    case AST_PACKAGE:
        compile_identifier(AST_GET_MEMBER(sn,0), OP_PUSHN);
        instr = next_instr(cu->curblock);
        instr->opcode = OP_PACKAGE;
        break;

    case AST_IMPORT:
        for (ii=0;ii<sn->size;ii++) {
            if (AST_GET_MEMBER(sn, ii)->type != AST_SYMBOL)
                compile_identifier(AST_GET_MEMBER(sn,ii), OP_PUSHN);
            else {
                idx = idx_in_consts("*");
                instr = next_instr(cu->curblock);
                instr->opcode = OP_PUSHC;
                SET_I_ARG(instr, idx);
            }
        }
        instr = next_instr(cu->curblock);
        instr->opcode = OP_MKLIST;
        SET_I_ARG(instr, sn->size);
        instr = next_instr(cu->curblock);
        instr->opcode = OP_IMPORT;
        break;

    case AST_INDEX:
        compile_ast_node(AST_GET_MEMBER(sn,0)); // the list/hash
        compile_ast_node(AST_GET_MEMBER(sn,1)); // the index
        instr = next_instr(cu->curblock);
        instr->opcode = OP_GET_INDEX;
        break;

    case AST_SLICE:
        compile_ast_node(AST_GET_MEMBER(sn,0)); // the list
        compile_ast_node(AST_GET_MEMBER(sn,1)); // the slice
        instr = next_instr(cu->curblock);
        instr->opcode = OP_MKLIST;
        SET_I_ARG(instr, 3);
        instr = next_instr(cu->curblock);
        instr->opcode = OP_GET_SLICE;
        break;

    case AST_IDXLIST:
        compile_ast_node(AST_GET_MEMBER(sn,0)); // the list
        compile_ast_node(AST_GET_MEMBER(sn,1)); // the idxlist
        instr = next_instr(cu->curblock);
        instr->opcode = OP_MKLIST;
        SET_I_ARG(instr, AST_GET_MEMBER(sn,1)->size);
        instr = next_instr(cu->curblock);
        instr->opcode = OP_GET_IDXLIST;
        break;

    case AST_RAISE:
        break;

    case AST_TRY:
        break;

    case AST_CATCH:
        break;

    case AST_FINALLY:
        break;

    case AST_CLASSDEF:
        /*
         * I planed to have every user class to be subclasses of "Object".
         * However, I am not sure how this should work.
         * So for simplicity, I am going to ignore Object as a superclass.
         */
        if (strcmp(AST_GET_LEXEME_SAFE(AST_GET_MEMBER(sn,1)), "Object") != 0) {
            compile_identifier(AST_GET_MEMBER(sn,1), OP_PUSH);
        } else {
            idx = idx_in_consts("null");
            instr = next_instr(cu->curblock);
            instr->opcode = OP_PUSHC;
            SET_I_ARG(instr, idx);
        }
        // class body
        compiler.cu = newcompiledunit();
        symtab = compiler.symtab;
        compiler.symtab = newhashobject();

        // Note we save the environment where the attributes, methods are defined
        ob = (EmObject *) compile_ast_unit(AST_GET_MEMBER(sn,2),1);

        // restore parent compiled unit
        compiler.cu = cu;
        compiler.symtab = symtab;

        // Add the code object that creates the class body
        listobject_append(cu->consts, ob);
        idx = listobject_len(cu->consts) - 1;
        DECREF(ob);
        instr = next_instr(cu->curblock);
        instr->opcode = OP_PUSHC;
        SET_I_ARG(instr, idx);

        // build a function to run the above code object
        instr = next_instr(cu->curblock);
        instr->opcode = OP_FUNCDEF;

        // push null arguments
        idx = idx_in_consts("null");
        instr = next_instr(cu->curblock);
        instr->opcode = OP_PUSHC;
        SET_I_ARG(instr, idx);

        // call the function to build class body, i.e. the env made of hash
        instr = next_instr(cu->curblock);
        instr->opcode = OP_CALL;

        // Build the class now
        instr = next_instr(cu->curblock);
        instr->opcode = OP_CLASSDEF;

        // store the class name
        compile_identifier(AST_GET_MEMBER(sn,0), OP_POP);

        break;

    default:
        break;
    }

}

static EmCodeObject *assemble(CompiledUnit *cu);

static EmCodeObject *
compile_ast_unit(AstNode *sn, int saveEnv) {
    int ii;
    for (ii = 0; ii < sn->size; ii++) {
        compile_ast_node(AST_GET_MEMBER(sn,ii));
    }

    if (saveEnv) {
        Instr *instr;
        instr = next_instr(compiler.cu->curblock);
        instr->opcode = OP_PUSH_ENV;
        instr = next_instr(compiler.cu->curblock);
        instr->opcode = OP_RETURN;
    }

    EmCodeObject *co = assemble(compiler.cu);
    freecompiledunit(compiler.cu);
    freeobj(compiler.symtab);
    return co;
}

static int compiler_init() {
    cur_row = 0;
    compiler.cu = newcompiledunit();
    compiler.symtab = newhashobject();
    return 1;
}

EmCodeObject *
compile_ast_tree(AstNode *stree) {

    EmCodeObject *co;
    compiler_init();

    if (setjmp(__compile_buf) == 0) {
        co = compile_ast_unit(stree, 0);
    } else {
        fatal("compiler error");
        fprintf(stderr, "ERROR compile\n");
        freecompiledunit(compiler.cu);
        compiler.cu = NULL;
    }

    return co;
}

static EmCodeObject *
assemble(CompiledUnit *cu) {
    int ii, nbytes, count, arg;
    Basicblock *b;
    Instr *instr;

    nbytes = 0;
    for (b = cu->block; b != NULL; b = b->next) {
        b->lineno = nbytes;
        count = 0;
        for (ii = 0; ii < b->inxt; ii++) {
            instr = INSTR_AT(b,ii);
            if (I_HASARG(instr)) {
                count += 3;
            } else {
                count += 1;
            }
        }
        nbytes += count;
    }

    // nbytes + 1 to insert an OP_END at the end
    EmCodeObject *co = (EmCodeObject *) newcodeobject(nbytes + 1);

    count = 0;
    for (b = cu->block; b != NULL; b = b->next) {
        for (ii = 0; ii < b->inxt; ii++) {
            instr = INSTR_AT(b,ii);
            // add op byte
            co->code[count++] = instr->opcode;
            if (I_HASARG(instr)) {
                if (I_ISJUMP(instr)) { // set jump lineno
                    arg = I_TARGET(instr)->lineno;
                } else { // regular arg
                    arg = I_ARG(instr);
                }
                co->code[count++] = arg & 0xff;
                co->code[count++] = arg >> 8;
            }
        }
    }
    co->code[count] = OP_END;

    co->consts = cu->consts;
    co->names = cu->names;

    cu->consts = NULL;
    cu->names = NULL;

    return co;
}

