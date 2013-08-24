/*
 * node.h
 * The parse tree node.
 *
 *  Created on: 04/08/2013
 *      Author: ywangd
 */

#ifndef NODE_H_
#define NODE_H_

#define NCH(n)          (n)->nchildren
// The ith child from the left, zero based
#define CHILD(n, i)     (&(n)->child[i])
// The ith child from the right, zero based
#define RCHILD(n, i)    (&(n)->child[(n)->nchildren-i-1])

extern char *node_types[];

typedef struct _node {
    int type;
    char *lexeme;
    int row;
    int col;
    int nchildren;
    struct _node *child;
} Node;

Node *newparsetree(int type);
Node *addchild(Node *parent, int type, char *lexeme, int row, int col);
void freetree(Node *ptree);
void printtree(Node *ptree);

#endif /* NODE_H_ */
