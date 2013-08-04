/*
 * node.h
 * The syntax tree node.
 *
 *  Created on: 04/08/2013
 *      Author: ywangd
 */

#ifndef NODE_H_
#define NODE_H_

#include "allobject.h"

typedef struct _node {
    int type;
    int row;
    int nchildren;
    struct _node *child;
} Node;

Node *newstringobject(int type);


#endif /* NODE_H_ */
