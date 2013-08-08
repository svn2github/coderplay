/*
 * ast.c
 *
 *  Created on: 08/08/2013
 *      Author: ywang@gmail.com
 */

#include "ast.h"

AstBase *
newastnode(int kind, int size) {
    AstBase *n;
    if ((n = (AstBase *) malloc(sizeof(AstBase))) == NULL) {
        log_error(MEMORY_ERROR, "not enough memory for new AST node");
        return NULL;
    }
    if (size > 0) {
        if ((n->child = (AstBase *) malloc(sizeof(AstBase) * size)) == NULL) {
            log_error(MEMORY_ERROR, "not enough memory for AST node subtree");
            return NULL;
        }
    } else
        n->child = NULL;
    n->size = size;
    n->type = type;
    return n;
}

//void print_snodes(AstBase *sn) {
//    int ii;
//    printf("(");
//    if (sn->size == 0) {
//        printf("%d", sn->type);
//    } else if (sn->size == 1) {
//        printf("%s", (char *)sn->child);
//    } else {
//        for (ii = 0; ii < sn->size; ii++) {
//            print_snodes(AST_GET_CHILD(sn, ii));
//            if (ii < sn->size - 1)
//                printf(",");
//        }
//    }
//    printf(")");
//}

void print_stree(AstBase *stree) {
    if (stree != NULL) {
        print_snodes(stree);
        printf("\n");
    }
}

AstBase *ast_from_pnode(Node *pn) {
    AstBase *sn = NULL;
    int ii;
    if (NCH(pn) == 1) {
        return ast_from_pnode(CHILD(pn,0));
    } else {
        sn = NULL;
        switch (pn->type) {
        case EXPR:
            sn = newastnode(AST_EXPR, 0);
            break;
        case PRINT_STMT:
            break;
        case RETURN_STMT:
            if (NCH(pn) == 0) {
                return newastnode(AST_RETURN, 0);
            } else {
                sn = newastnode(AST_RETURN, 1);
                AST_SET_CHILD(sn, 0, ast_from_pnode(CHILD(pn,0)));
            }
            break;
        case INTEGER:
            sn = newastnode(AST_INT, 1);
            AST_SET_CHILD(sn, 0, pn->lexeme);
            pn->lexeme = NULL;
            break;
        default:
            break;
        }
        return sn;
    }
}

AstBase *ast_from_ptree(Node *ptree) {
    AstSeq *stree = NEW_AST_NODE(AstSeq);
    int ii;
    for (ii = 0; ii < NCH(ptree); ii++) {
        //AST_SET_CHILD(stree, ii, ast_from_pnode(CHILD(ptree, ii)));
    }
    return stree;
}
