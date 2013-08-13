/*
 * compiler.h
 *
 *  Created on: 12/08/2013
 *      Author: ywangd
 */

#ifndef COMPILER_H_
#define COMPILER_H_



typedef struct _instr {
    int opcode;
    union {
        int arg;
        struct _basic_block *target;
    } v;
    int row;
    int col;
} Instr;

typedef struct _basic_block {
    int lineno;         // starting line number of opcode list in this block
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
