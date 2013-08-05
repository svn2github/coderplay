/*
 * node.c
 *
 *  Created on: 04/08/2013
 *      Author: ywangd
 */
#include "node.h"

#define TOKEN_BASE      256
#define NODE_BASE       1000


Node *newparsetree(int type) {
    Node *n;
    if ((n = (Node *) malloc(sizeof(Node))) == NULL) {
        return log_error(MEMORY_ERROR, "not enough memory for parse tree");
    }
    n->type = type;
    n->lexeme = NULL;
    n->row = 0;
    n->nchildren = 0;
    n->child = NULL;
    return n;
}

Node *addchild(Node *p, int type, char *lexeme, unsigned int row) {
    Node *c; // child node

    // parent node
    if (p->nchildren == 0) {
        if ((p->child = (Node *) malloc(sizeof(Node))) == NULL) {
            return log_error(MEMORY_ERROR,
                    "not enough memory for adding child node");
        }
    } else {
        c = p->child;
        if ((c = (Node *) realloc(c, (p->nchildren + 1) * sizeof(Node))) == NULL) {
            return log_error(MEMORY_ERROR,
                    "not enough memory for adding child node");
        }
        p->child = c;
    }
    p->nchildren++;

    // The just added child node
    c = &p->child[p->nchildren - 1];
    c->type = type;
    if (lexeme) {
        if ((c->lexeme = (char *) malloc(strlen(lexeme) + 1)) == NULL) {
            return log_error(MEMORY_ERROR, "no memory to copy lexeme for node");
        }
        strcpy(c->lexeme, lexeme);
    } else {
        c->lexeme = NULL;
    }
    c->row = row;
    c->nchildren = 0;
    c->child = NULL;
    return c;
}

static void freechildren(Node *n) {
    int ii;
    for (ii = n->nchildren - 1; ii >= 0; ii--)
        freechildren(&n->child[ii]);
    if (n->child != NULL) {
        free(n->child);
        n->child = NULL;
    }
    if (n->lexeme != NULL) {
        free(n->lexeme);
        n->lexeme = NULL;
    }
}

void freetree(Node *ptree) {
    if (ptree != NULL) {
        freechildren(ptree);
        free(ptree);
        ptree = NULL;
    }
}

static int nlevels;

static void printchildren(Node *n) {

    int ii;

    nlevels++;

    if (n->type >= NODE_BASE) {
        printf("%s(", node_types[n->type-NODE_BASE]);
    } else if (n->type >= TOKEN_BASE) {
        printf("%s(", token_types[n->type-TOKEN_BASE]);
    } else {
        printf("%c", n->type);
    }

    if (nlevels == 1) {
        printf("\n");
    }

    if (n->lexeme)
        printf("%s", n->lexeme);

    for (ii=0;ii<n->nchildren;ii++) {
        printchildren(&n->child[ii]);
        if (ii<n->nchildren-1)
            printf(",");
    }
    if (n->type >= TOKEN_BASE)
        printf(")");

    nlevels--;

    if (nlevels == 1) {
        printf("\n");
    }

}

void printtree(Node *ptree) {
    if (ptree != NULL) {
        nlevels = 0;
        printchildren(ptree);
        printf("\n");
    }
}

