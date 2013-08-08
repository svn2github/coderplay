/*
 * ast.h
 *
 *  Created on: 08/08/2013
 *      Author: ywang@gmail.com
 */

#ifndef AST_H_
#define AST_H_

#include "Emma.h"
#include "ast.hi"

#define AST_SET_CHILD(n,i,c)       *((void **)((n)->child + ii)) = c
#define AST_GET_CHILD(n,i)         &(n)->child[i]

#define NEW_AST_NODE(type, kind)      malloc(sizeof(type))

#define



#define AST_NODE_HEAD       int kind; int row; int col



/*
 * Basic form of AST node
 * includes continue, break
 */
typedef struct _ast_base {
    AST_NODE_HEAD;
} AstBase;


/*
 * Meta-type: sequence members are separated by EOL
 * Module
 */
typedef struct _ast_seq {
    AST_NODE_HEAD;
    int size;
    AstBase *member;
} AstSeq;


/*
 * Meta-type: list members are separated by comma
 * Can be used for print, read, return, package, import, raise
 */
typedef struct _ast_list {
    AST_NODE_HEAD;
    int size;
    AstBase *member;
} AstList;


typedef struct _ast_assign {
    AST_NODE_HEAD;
    AstBase *target;
    AstBase *value;
} AstAssign;

typedef struct _ast_binop {
    AST_NODE_HEAD;
    int op;
    AstBase *loperand;
    AstBase *roperand;
} AstBinop;

typedef struct _ast_unaryop {
    AST_NODE_HEAD;
    int op;
    AstBase *operand;
} AstUnaryop;

typedef struct _ast_call {
    AST_NODE_HEAD;
    AstBase *func;
    AstList *args;
} AstCall;

typedef struct _ast_sub {
    AST_NODE_HEAD;
    AstBase *vector;
    AstBase *idx;
} AstSub;

typedef struct _ast_slice {
    AST_NODE_HEAD;
    AstBase *vector;
    AstBase *start;
    AstBase *end;
    AstBase *step;
} AstSlice;

typedef struct _ast_slist {
    AST_NODE_HEAD;
    AstBase *vector;
    AstList *idxlist;
} AstSlist;

typedef struct _ast_field {
    AST_NODE_HEAD;
    AstBase *obj;
    AstBase *field;
} AstField;

typedef struct _ast_ident {
    AST_NODE_HEAD;
    char *lexeme;
} AstIdent;

typedef struct _ast_literal {
    AST_NODE_HEAD;
    char *lexeme;
} AstLiteral;

typedef struct _ast_if {
    AST_NODE_HEAD;
    AstBase *test;
    AstSeq *tbody;
    AstSeq *fbody;
} AstIf;

typedef struct _ast_while {
    AST_NODE_HEAD;
    AstBase *test;
    AstSeq *body;
} AstWhile;

typedef struct _ast_for {
    AST_NODE_HEAD;
    AstBase *counter;
    AstBase *start;
    AstBase *end;
    AstBase *step;
    AstSeq *body;
} AstFor;

typedef struct _ast_funcdef {
    AST_NODE_HEAD;
    AstIdent *func;
    AstList *params;
    AstSeq *body;
} AstFuncDef;

typedef struct _ast_classdef {
    AST_NODE_HEAD;
    AstIdent *class;
    AstIdent *super;
    AstSeq *body;
} AstClassdef;

typedef struct _ast_catch {
    AST_NODE_HEAD;
    AstIdent *exception;
    AstIdent *var;
    AstSeq *body;
} AstCatch;

typedef struct _ast_try {
    AST_NODE_HEAD;
    AstSeq *body;
    AstSeq *catch;
    AstSeq *finally;
} AstTry;

typedef struct _ast_kvpair {
    AST_NODE_HEAD;
    AstIdent *key;
    AstBase *value;
} AstKvpair;

typedef struct _ast_extrap {
    AST_NODE_HEAD;
    AstIdent *extrap;
} AstExtrap;

typedef struct _ast_extrak {
    AST_NODE_HEAD;
    AstIdent *extrak;
} AstExtrak;



AstBase *ast_from_ptree(Node *ptree);


#endif /* AST_H_ */
