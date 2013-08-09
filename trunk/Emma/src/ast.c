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
        printf("member\n");
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
        free(stree);
    }
}

static void
set_snode_from_pnode(AstNode *sn, int idx, Node *pn) {

    int ii;

    if (NCH(pn) == 1) {
        /*
         * If the parse node has only 1 child, we skip it and directly process
         * the child node.
         */
        set_snode_from_pnode(sn, idx, CHILD(pn,0));

    } else if (NCH(pn) == 0) { // only literals have no child
        printf("only here once\n");
        AST_GET_MEMBER(sn, idx) = newastnode(AST_LITERAL, 0);
        AST_GET_MEMBER(sn, idx)->row = pn->row;
        AST_GET_MEMBER(sn, idx)->col = pn->col;
        AST_GET_MEMBER(sn, idx)->lexeme = pn->lexeme;
        pn->lexeme = NULL;

    } else {
        printf("here\n");
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
                //AST_SET_MEMBER(sn, 0, newastnode_literal("null"));
            } else {
               //AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,0)));
            }
            break;
        default:
            break;
        }
    }
}

AstNode *ast_from_ptree(Node *ptree) {
    AstNode *stree = newastnode(AST_SEQ, NCH(ptree));
    stree->row = ptree->row;
    stree->col = ptree->col;
    int ii;
    AstNode *temp;
    for (ii = 0; ii < NCH(ptree); ii++) {
        set_snode_from_pnode(stree, ii, CHILD(ptree, ii));
    }
    return stree;
}
