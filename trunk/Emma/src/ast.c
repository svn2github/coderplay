/*
 * ast.c
 *
 *  Created on: 08/08/2013
 *      Author: ywang@gmail.com
 */

#include "ast.h"

AstNode *
newastnode(int type, int size) {
    AstNode *n;
    if ((n = (AstNode *) malloc(sizeof(AstNode))) == NULL) {
        log_error(MEMORY_ERROR, "not enough memory for new AST node");
        return NULL;
    }
    if (size > 0) {
        if ((n->members = (AstNode **) malloc(sizeof(AstNode *) * size)) == NULL) {
            log_error(MEMORY_ERROR, "not enough memory for AST node subtree");
            return NULL;
        }
    } else {
        n->lexeme = NULL;
    }
    n->size = size;
    n->type = type;
    return n;
}

AstNode *
newastnode_literal(char *lexeme) {
    AstNode *n;
    if ((n = (AstNode *) malloc(sizeof(AstNode))) == NULL) {
        log_error(MEMORY_ERROR, "not enough memory for new AST node");
        return NULL;
    }
    n->type = AST_LITERAL;
    n->size = 0;
    n->lexeme = lexeme;
    return n;
}

static void printsnodes(AstNode *sn) {
    int ii;
    if (sn->size == 0) {
        printf("(literal %s)", sn->lexeme);
    } else {
        printf("(%d ", sn->type);
        for (ii = 0; ii < sn->size; ii++) {
            printsnodes(AST_GET_MEMBER(sn, ii));
        }
        printf(")");
    }
}

void printstree(AstNode *stree) {
    if (stree != NULL) {
        printsnodes(stree);
        printf("\n");
    }
}

static void freemembers(AstNode *sn) {
    int ii;
    if (sn->size > 0) {
        for (ii = sn->size - 1; ii >= 0; ii--) {
            freemembers(AST_GET_MEMBER(sn,ii));
        }
        free(sn->members);
    } else {
        free(sn->lexeme);
    }
}

void freestree(AstNode *stree) {
    if (stree != NULL) {
        freemembers(stree);
    }
}

static AstNode *
ast_from_pnode(Node *pn) {
    AstNode *sn = NULL;
    int ii;
    /*
     * If the parse node has only 1 child, we skip it and directly process
     * the child node.
     */
    if (NCH(pn) == 1) {
        return ast_from_pnode(CHILD(pn,0));
    } else if (NCH(pn) == 0) { // only literals have no child
        sn = newastnode(AST_LITERAL, 0);
        sn->row = pn->row;
        sn->col = pn->col;
        sn->lexeme = pn->lexeme;
        pn->lexeme = NULL;
    } else {
        sn->row = pn->row;
        sn->col = pn->col;
        switch (pn->type) {
        case EXPR:
            break;
        case PRINT_STMT:
            break;
        case RETURN_STMT:
            sn = newastnode(AST_RETURN, 1);
            if (NCH(pn) == 0) {
                AST_SET_MEMBER(sn, 0, newastnode_literal("null"));
            } else {
                AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,0)));
            }
            break;
        default:
            break;
        }
    }
    return sn;
}

AstNode *ast_from_ptree(Node *ptree) {
    AstNode *stree = newastnode(AST_SEQ, NCH(ptree));
    stree->row = ptree->row;
    stree->col = ptree->col;
    int ii;
    for (ii = 0; ii < NCH(ptree); ii++) {
        AST_SET_MEMBER(stree, ii, ast_from_pnode(CHILD(ptree, ii)));
    }
    return stree;
}
