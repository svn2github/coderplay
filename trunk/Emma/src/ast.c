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
        if ((n->v.members = (AstNode **) malloc(sizeof(AstNode *) * size)) == NULL) {
            log_error(MEMORY_ERROR, "not enough memory for AST node subtree");
            return NULL;
        }
    } else {
        n->v.lexeme = NULL;
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
    n->v.lexeme = lexeme;
    return n;
}

static void printsnodes(AstNode *sn) {
    int ii;
    if (sn->size == 0) {
        printf("(literal %s)", AST_GET_LEXEME(sn));
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
            free(AST_GET_MEMBER(sn,ii));
        }
        free(sn->v.members);
    } else {
        free(sn->v.lexeme);
    }
}

void freestree(AstNode *stree) {
    if (stree != NULL) {
        freemembers(stree);
        free(stree);
    }
}

static AstNode *
ast_from_pnode(Node *pn) {

    AstNode *sn = NULL;
    int ii;

    if (NCH(pn) == 1) {
        /*
         * If the parse node has only 1 child, we skip it and directly process
         * the child node.
         */
        return ast_from_pnode(CHILD(pn, 0));

    } else if (NCH(pn) == 0) { // only literals have no child
        sn = newastnode_literal(pn->lexeme);
        pn->lexeme = NULL;
        sn->row = pn->row;
        sn->col = pn->col;

    } else {
        switch (pn->type) {
        case EXPR:
            break;
        case PRINT_STMT:
            break;
        case RETURN_STMT:
            sn = newastnode(AST_RETURN, 1);
            if (NCH(pn) == 0) {
                AST_SET_MEMBER(sn, 0, newastnode_literal(NULL));
            } else {
                AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,0)));
            }
            break;
        default:
            break;
        }
        sn->row = pn->row;
        sn->col = pn->col;
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
