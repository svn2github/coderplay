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

#define AST_SET_MEMBER(n,i,c)       (n)->members[i] = c
#define AST_GET_MEMBER(n,i)         ((n)->members[i])

#define AST_NODE_HEAD       int kind; int row; int col

typedef struct _ast_node {
    int type;
    int row;
    int col;
    int size;

    struct _ast_node **members;
    char *lexeme;

} AstNode;

AstNode *ast_from_ptree(Node *ptree);
void freestree(AstNode *stree);
void printstree(AstNode *stree);

#endif /* AST_H_ */
