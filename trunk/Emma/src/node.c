/*
 * node.c
 *
 *  Created on: 04/08/2013
 *      Author: ywangd
 */
#include "node.h"

Node *newsyntaxtree(int type) {
    Node *node;
    if ((node = (Node *)malloc(sizeof(Node))) == NULL) {
        return log_error(MEMORY_ERROR, "not enough memory for syntax tree");
    }
    node->type = type;
    node->row = 0;
    node->nchildren = 0;
    node->child = NULL;
    return node;
}
