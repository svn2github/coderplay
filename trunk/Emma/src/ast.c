/*
 * ast.c
 *
 *  Created on: 08/08/2013
 *      Author: ywang@gmail.com
 */

#include "ast.h"
#include "ast.i"

static AstNode *
newastnode(int type, int size, unsigned int row, unsigned int col) {
    AstNode *n;
    if ((n = (AstNode *) malloc(sizeof(AstNode))) == NULL) {
        log_error(MEMORY_ERROR, "not enough memory for new AST node");
        return NULL;
    }
    if (size > 0) {
        if ((n->v.members = (AstNode **) malloc(sizeof(AstNode *) * size))
                == NULL) {
            log_error(MEMORY_ERROR, "not enough memory for AST node subtree");
            return NULL;
        }
    } else {
        n->v.lexeme = NULL;
    }

    n->size = size;
    n->type = type;
    n->row = row;
    n->col = col;
    return n;
}

static void printsnodes(AstNode *sn) {
    int ii;
    if (sn->size == 0) {
        printf("(%s %s)", snode_types[sn->type],
        AST_GET_LEXEME(sn) ? AST_GET_LEXEME(sn) : "null");
    } else {
        printf("(%s ", snode_types[sn->type]);
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

    switch (pn->type) {

    case STATEMENT:
    case SIMPLE_STMT:
    case COMPOUND_STMT:
    case EXPR:
        sn = ast_from_pnode(CHILD(pn, 0));
        break;

    case ASSIGN_STMT:
        break;

    case PRINT_STMT:
        break;

    case READ_STMT:
        break;

    case CONTINUE_STMT:
        break;

    case BREAK_STMT:
        break;

    case RETURN_STMT:
        sn = newastnode(AST_RETURN, 1, pn->row, pn->col);
        if (NCH(pn) == 1) {
            AST_SET_MEMBER(sn, 0, newastnode(AST_LITERAL, 0, pn->row, pn->col));
        } else {
            AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,1)));
        }
        break;

    case PACKAGE_STMT:
        break;

    case IMPORT_STMT:
        break;

    case RAISE_STMT:
        break;

    case TRAILER:
        break;

    case IF_STMT:
        break;

    case WHILE_STMT:
        break;

    case FOR_STMT:
        break;

    case FUNCDEF:
        break;

    case CLASSDEF:
        break;

    case TRY_STMT:
        break;

    case CATCH_STMT:
        break;

    case FINALLY_STMT:
        break;

    case SUITE:
        break;

    case STMT_BLOCK:
        break;

    case FOR_EXPR:
        break;

    case R_EXPR:
        if (NCH(pn) == 1)
            sn = ast_from_pnode(CHILD(pn, 0));
        break;

    case R_TERM:
        if (NCH(pn) == 1)
            sn = ast_from_pnode(CHILD(pn, 0));
        break;

    case R_FACTOR:
        if (NCH(pn) == 1)
            sn = ast_from_pnode(CHILD(pn, 0));
        break;

    case L_EXPR:
        if (NCH(pn) == 1)
            sn = ast_from_pnode(CHILD(pn, 0));
        break;

    case A_EXPR:
        if (NCH(pn) == 1)
            sn = ast_from_pnode(CHILD(pn, 0));
        break;

    case A_TERM:
        if (NCH(pn) == 1)
            sn = ast_from_pnode(CHILD(pn, 0));
        break;

    case FACTOR:
        if (NCH(pn) == 1)
            sn = ast_from_pnode(CHILD(pn, 0));
        break;

    case POWER:
        if (NCH(pn) == 1)
            sn = ast_from_pnode(CHILD(pn, 0));
        break;

    case PRIMARY:
        if (NCH(pn) == 1)
            sn = ast_from_pnode(CHILD(pn, 0));
        break;

    case ATOM:
        if (NCH(pn) == 1)
            sn = ast_from_pnode(CHILD(pn, 0));
        break;

    case EXPR_LIST:
        break;

    case PARMLIST:
        break;

    case OPARM_LIST:
        break;

    case OPARM:
        break;

    case KVPAIR:
        break;

    case ARGLIST:
        break;

    case OARG:
        break;

    case SUBSCRIPTION:
        break;

    case SINGLEIDX:
        break;

    case IDXRANGE:
        break;

    case IDXLIST:
        break;

    default:
        /*
         * Anything left here should be literals and indentifier
         */
        if (pn->type == IDENT) {
            sn = newastnode(AST_IDENT, 0, pn->row, pn->col);
            AST_SET_LEXEME(sn, pn->lexeme);
        } else if (pn->type == INTEGER || pn->type == FLOAT
                || pn->type == STRING) {
            sn = newastnode(AST_LITERAL, 0, pn->row, pn->col);
            AST_SET_LEXEME(sn, pn->lexeme);
        } else if (pn->type == NUL) {
            sn = newastnode(AST_LITERAL, 0, pn->row, pn->col);
        } else {
            printf("something is wrong\n");
            exit(1);
        }

        break;
    }
    return sn;
}

AstNode *ast_from_ptree(Node *ptree) {
    AstNode *stree = newastnode(AST_SEQ, NCH(ptree), ptree->row, ptree->col);
    int ii;
    for (ii = 0; ii < NCH(ptree); ii++) {
        AST_SET_MEMBER(stree, ii, ast_from_pnode(CHILD(ptree, ii)));
    }
    return stree;
}
