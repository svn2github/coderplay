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

typedef struct _ast_node {
    int type;
    int size;
    struct _ast_node *child;
} AstNode;

//AstNode *ast_from_ptree(Node *ptree);


#endif /* AST_H_ */
