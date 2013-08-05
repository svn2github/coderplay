/*
 * node.h
 * The parse tree node.
 *
 *  Created on: 04/08/2013
 *      Author: ywangd
 */

#ifndef NODE_H_
#define NODE_H_

#include "allobject.h"

extern char *node_types[];

typedef struct _node {
    int type;
    char *lexeme;
    int row;
    int nchildren;
    struct _node *child;
} Node;

Node *newparsetree(int type);
Node *addchild(Node *parent, int type, char *lexeme, unsigned int row);
void freetree(Node *ptree);
void printtree(Node *ptree);

#endif /* NODE_H_ */
