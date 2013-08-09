/*
 * ast.c
 *
 *  Created on: 08/08/2013
 *      Author: ywang@gmail.com
 */

#include "ast.h"
#include "ast.i"

#define AST_TYPE_OF_R_EXPR(t,n,i)   t=CHILD(n,i)->type==OR?AST_OR:AST_XOR

#define AST_TYPE_OF_L_EXPR(t,n,i)   if (CHILD(n,i)->type=='>') t=AST_GT; \
                                        else if (CHILD(n,i)->type==GE) t=AST_GE; \
                                        else if (CHILD(n,i)->type=='<') t=AST_LT; \
                                        else if (CHILD(n,i)->type==LE) t=AST_LE; \
                                        else if (CHILD(n,i)->type==EQ) t=AST_EQ; \
                                        else t=AST_NE;

#define AST_TYPE_OF_A_EXPR(t,n,i)   t=CHILD(n,i)->type=='+'?AST_ADD:AST_SUB


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
        n->v.symbol = '\0';
    }

    n->size = size;
    n->type = type;
    n->row = row;
    n->col = col;
    return n;
}

static void printsnodes(AstNode *sn) {
    int ii;
    if (sn->size == 0 && sn->type != AST_SYMBOL) {
        printf("(%s %s)", snode_types[sn->type],
        AST_GET_LEXEME(sn) ? AST_GET_LEXEME(sn) : "null");

    } else if (sn->type == AST_SYMBOL) {
        printf("(%s %c)", snode_types[sn->type], AST_GET_SYMBOL(sn));

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

    AstNode *sn = NULL, *sn_temp = NULL;
    int ii, jj, stype;

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
        sn = newastnode(AST_CONTINUE, 0, pn->row, pn->col);
        break;

    case BREAK_STMT:
        sn = newastnode(AST_BREAK, 0, pn->row, pn->col);
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
        sn = newastnode(AST_PACKAGE, 1, pn->row, pn->col);
        AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,1)));
        break;

    case IMPORT_STMT:
        sn = newastnode(AST_IMPORT, NCH(pn) / 2, pn->row, pn->col);
        for (ii = 1, jj = 0; ii < NCH(pn) && jj < sn->size; ii += 2, jj++) {
            AST_SET_MEMBER(sn, jj, ast_from_pnode(CHILD(pn,ii)));
        }
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
        else {
            for (ii = 1; ii < NCH(pn) - 1; ii += 2) {
                sn_temp = sn;
                AST_TYPE_OF_R_EXPR(stype, pn, ii);
                sn = newastnode(stype, 2, CHILD(pn,ii)->row, CHILD(pn,ii)->col);
                if (sn_temp == NULL)
                    AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,ii-1)));
                else
                    AST_SET_MEMBER(sn, 0, sn_temp);
                AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,ii+1)));
            }
        }
        break;

    case R_TERM:
        if (NCH(pn) == 1)
            sn = ast_from_pnode(CHILD(pn, 0));
        else {
            for (ii = 1; ii < NCH(pn) - 1; ii += 2) {
                sn_temp = sn;
                sn = newastnode(AST_AND, 2, CHILD(pn,ii)->row,
                        CHILD(pn,ii)->col);
                if (sn_temp == NULL)
                    AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,ii-1)));
                else
                    AST_SET_MEMBER(sn, 0, sn_temp);
                AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,ii+1)));
            }
        }
        break;

    case R_FACTOR:
        if (NCH(pn) == 1)
            sn = ast_from_pnode(CHILD(pn, 0));
        else {
            sn = newastnode(AST_NOT, 1, pn->row, pn->col);
            AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,1)));
        }
        break;

    case L_EXPR:
        if (NCH(pn) == 1)
            sn = ast_from_pnode(CHILD(pn, 0));
        else {
            for (ii = 1; ii < NCH(pn) - 1; ii += 2) {
                sn_temp = sn;
                AST_TYPE_OF_L_EXPR(stype, pn, ii);
                sn = newastnode(stype, 2, CHILD(pn,ii)->row, CHILD(pn,ii)->col);
                if (sn_temp == NULL)
                    AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,ii-1)));
                else
                    AST_SET_MEMBER(sn, 0, sn_temp);
                AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,ii+1)));
            }
        }
        break;

    case A_EXPR:
        if (NCH(pn) == 1)
            sn = ast_from_pnode(CHILD(pn, 0));
        else {
            for (ii = 1; ii < NCH(pn) - 1; ii += 2) {
                sn_temp = sn;
                AST_TYPE_OF_A_EXPR(stype, pn, ii);
                sn = newastnode(stype, 2, CHILD(pn,ii)->row, CHILD(pn,ii)->col);
                if (sn_temp == NULL)
                    AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,ii-1)));
                else
                    AST_SET_MEMBER(sn, 0, sn_temp);
                AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,ii+1)));
            }
        }
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
        else { // (...) expr
            sn = ast_from_pnode(CHILD(pn, 1));
        }
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

    case '*':
        sn = newastnode(AST_SYMBOL, 0, pn->row, pn->col);
        AST_SET_SYMBOL(sn, '*');
        break;

    case IDENT:
        sn = newastnode(AST_IDENT, 0, pn->row, pn->col);
        AST_SET_LEXEME(sn, pn->lexeme)
        ;
        break;

    case INTEGER:
    case FLOAT:
    case STRING:
        sn = newastnode(AST_LITERAL, 0, pn->row, pn->col);
        AST_SET_LEXEME(sn, pn->lexeme)
        ;
        break;

    case NUL:
        sn = newastnode(AST_LITERAL, 0, pn->row, pn->col);
        break;

    default:
        fprintf(stderr, "something wrong!\n");
        exit(1);
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
