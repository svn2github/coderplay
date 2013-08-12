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

#define AST_SET_MEMBER(n,i,c)       (n)->v.members[i] = c
#define AST_GET_MEMBER(n,i)         ((n)->v.members[i])

#define AST_GET_LEXEME(n)           (n)->v.lexeme
#define AST_SET_LEXEME(n,s)         (n)->v.lexeme = s; s = NULL

#define AST_GET_LEXEME_SAFE(n)      ((n)->v.lexeme?(n)->v.lexeme:"null")

#define AST_GET_SYMBOL(n)           (n)->v.symbol
#define AST_SET_SYMBOL(n,s)         (n)->v.symbol = s

typedef struct _ast_node {
    int type;
    unsigned int row;
    unsigned int col;
    int size;

    /*
     * It is not necessary to use union for two pointer type variables.
     * A void pointer is good enough to represent both of them. However,
     * It is more readale to use union and have two different variable
     * names.
     */
    union {
        struct _ast_node **members;
        char *lexeme; // literal and ident
        int symbol;
    } v;

} AstNode;

AstNode *ast_from_ptree(Node *ptree);
void freestree(AstNode *stree);
void printstree(AstNode *stree);

#endif /* AST_H_ */
