/*
 * compiler.h
 *
 *  Created on: 12/08/2013
 *      Author: ywangd
 */

#ifndef COMPILER_H_
#define COMPILER_H_

#define DEFAULT_BLOCK_SIZE      16

#define GET_INSTR_FROM_BLOCK(b,i)       (&(b)->instrlist[i])
#define I_STR(instr)    opcode_types[instr->opcode]
#define I_ARG(instr)    instr->v.arg
#define I_TARGET(instr)    instr->v.target


typedef struct _instr {
    unsigned isjump :1;     // this member use one bit
    unsigned hasarg :1;
    int opcode;
    union {
        int arg;
        struct _basic_block *target;
    } v;
    int row;
    int col;
} Instr;

typedef struct _basic_block {
    struct _basic_block *next;
    Instr *instrlist;
    int inxt;   // next instruction
    int ilen;   // length of instruction
} Basicblock;

typedef struct _compiled_unit {
    Basicblock *block;      // linked list of blocks
    Basicblock *curblock;   // the current used block
    EmObject *consts;       // list of constants and compiled functions
    EmObject *names;        // list of variable names
} CompiledUnit;

typedef struct _compiler {
    CompiledUnit *cu;
} Compiler;


void freecompiledunit(CompiledUnit *cu);
void printcompiledunit(CompiledUnit *cu);
CompiledUnit *compile_ast(AstNode *);

#endif /* COMPILER_H_ */
