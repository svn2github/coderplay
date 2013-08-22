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
} Instr;

typedef struct _basic_block {
    int lineno;         // starting line number of opcode list in this block
    struct _basic_block *next;
    Instr *instrlist;
    int inxt;   // next instruction
    int ilen;   // length of instruction
} Basicblock;

# define MAX_NEST_LEVEL         50

typedef struct _compiled_unit {
    Basicblock *block;      // linked list of blocks
    Basicblock *curblock;   // the current used block
    EmObject *consts;       // list of constants and compiled functions
    EmObject *names;        // list of variable names
    Basicblock **continueblock;
    Basicblock **breakblock;
    int i_continueblock;
    int i_breakblock;
} CompiledUnit;

typedef struct _compiler {
    CompiledUnit *cu;
    EmObject *symtab; // The symbol table for compilation
} Compiler;


void freecompiledunit(CompiledUnit *cu);
void printcompiledunit(CompiledUnit *cu);
EmCodeObject *compile_ast_tree(AstNode *);

#endif /* COMPILER_H_ */
