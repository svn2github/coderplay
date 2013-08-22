/*
 * ast.c
 *
 *  Created on: 08/08/2013
 *      Author: ywang@gmail.com
 */

#include "Emma.h"
#include "ast.i"

#define AST_TYPE_OF_BINOP(t,n,i)    if (CHILD(n,i)->type==OR) t=AST_OR; \
                                        else if (CHILD(n,i)->type==XOR) t=AST_XOR; \
                                        else if (CHILD(n,i)->type==AND) t=AST_AND; \
                                        else if (CHILD(n,i)->type=='>') t=AST_GT; \
                                        else if (CHILD(n,i)->type==GE) t=AST_GE; \
                                        else if (CHILD(n,i)->type=='<') t=AST_LT; \
                                        else if (CHILD(n,i)->type==LE) t=AST_LE; \
                                        else if (CHILD(n,i)->type==EQ) t=AST_EQ; \
                                        else if (CHILD(n,i)->type==NE) t=AST_NE; \
                                        else if (CHILD(n,i)->type=='+') t=AST_ADD; \
                                        else if (CHILD(n,i)->type=='-') t=AST_SUB; \
                                        else if (CHILD(n,i)->type=='*') t=AST_MUL; \
                                        else if (CHILD(n,i)->type=='/') t=AST_DIV; \
                                        else if (CHILD(n,i)->type=='%') t=AST_MOD; \
                                        else if (CHILD(n,i)->type==DSTAR) t=AST_POW; \
                                        else fatal("unrecognized binary operator");

#define AST_TYPE_OF_UNARYOP(t,n,i)  if (CHILD(n,i)->type==NOT) t=AST_NOT; \
                                        else if (CHILD(n,i)->type=='+') t=AST_PLUS; \
                                        else if (CHILD(n,i)->type=='-') t=AST_MINUS; \
                                        else fatal("unrecognized unary operator");

#define AST_TYPE_OF_TRAILER(t,n,i) if (CHILD(n,i)->type=='(') t=AST_CALL; \
                                        else if (CHILD(n,i)->type=='.') t=AST_FIELD; \
                                        else { \
                                            if (CHILD(CHILD(pn,i+1),0)->type == SINGLEIDX) t=AST_INDEX; \
                                            else if (CHILD(CHILD(pn,i+1),0)->type == IDXRANGE) t=AST_SLICE; \
                                            else if (CHILD(CHILD(pn,i+1),0)->type == IDXLIST) t=AST_IDXLIST; \
                                            else fatal("unrecognized trailer"); \
                                        }

static char *
get_strp(char *s) {
    char *copys;
    copys = (char*) malloc(sizeof(char) * (strlen(s) + 1));
    if (copys == NULL)
        return log_error(MEMORY_ERROR, "Not enough memory for string copy");
    return strcpy(copys, s);
}

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

static int level;

static void printsnodes(AstNode *sn) {
    int ii;
    level++;
    if (sn->type == AST_LITERAL || sn->type == AST_IDENT) {
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
    level--;
    if (level == 1)
        printf("\n");
}

void printstree(AstNode *stree) {
    if (stree != NULL) {
        level = 0;
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
        if (sn->type == AST_IDENT || sn->type == AST_LITERAL)
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

    AstNode *sn = NULL, *sn_left = NULL, *sn_temp = NULL;
    int ii, jj, stype;

    switch (pn->type) {

    case STATEMENT:
    case COMPOUND_STMT:
    case EXPR:
        sn = ast_from_pnode(CHILD(pn, 0));
        break;

    case SIMPLE_STMT:
        if (CHILD(pn,0)->type == EXPR) {
            /*
             * Always assign stand alone expression value to special
             * variable "_".
             */
            if (source.type == SOURCE_TYPE_PROMPT) {
                sn = newastnode(AST_SEQ, 2, pn->row, pn->col);
                sn_temp = newastnode(AST_ASSIGN, 2, pn->row, pn->col);
                AST_SET_MEMBER(sn_temp, 0,
                        newastnode(AST_IDENT, 0, pn->row, pn->col));
                AST_GET_MEMBER(sn_temp,0)->v.lexeme = get_strp("_");
                AST_SET_MEMBER(sn_temp, 1, ast_from_pnode(CHILD(pn, 0)));
                AST_SET_MEMBER(sn, 0, sn_temp);

                sn_temp = newastnode(AST_PRINT, 2, pn->row, pn->col);
                AST_SET_MEMBER(sn_temp, 0,
                        newastnode(AST_IDENT, 0, pn->row, pn->col));
                AST_GET_MEMBER(sn_temp, 0)->v.lexeme = get_strp("stdout");
                AST_SET_MEMBER(sn, 1, sn_temp);
                sn_temp = newastnode(AST_LIST, 1, pn->row, pn->col);
                AST_SET_MEMBER(sn_temp, 0,
                        newastnode(AST_IDENT, 0, pn->row, pn->col));
                AST_GET_MEMBER(sn_temp, 0)->v.lexeme = get_strp("_");
                AST_SET_MEMBER(AST_GET_MEMBER(sn, 1), 1, sn_temp);
            } else {
                sn = newastnode(AST_ASSIGN, 2, pn->row, pn->col);
                AST_SET_MEMBER(sn, 0,
                        newastnode(AST_IDENT, 0, pn->row, pn->col));
                AST_GET_MEMBER(sn,0)->v.lexeme = get_strp("_");
                AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn, 0)));
            }
        } else {
            sn = ast_from_pnode(CHILD(pn, 0));
        }
        break;

    case ASSIGN_STMT:
        sn = newastnode(AST_ASSIGN, 2, pn->row, pn->col);
        AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,0)));
        AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,2)));
        break;

    case PRINT_STMT:
        sn = newastnode(AST_PRINT, 2, pn->row, pn->col);
        if (NCH(pn) == 2) { // default stdout
            AST_SET_MEMBER(sn, 0, newastnode(AST_IDENT, 0, pn->row, pn->col));
            AST_GET_MEMBER(sn, 0)->v.lexeme = get_strp("stdout");
            AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,1)));
        } else {
            AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,2)));
            AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,3)));
        }
        break;

    case READ_STMT:
        sn = newastnode(AST_READ, 2, pn->row, pn->col);
        if (NCH(pn) == 2) { // default stdout
            AST_SET_MEMBER(sn, 0, newastnode(AST_IDENT, 0, pn->row, pn->col));
            AST_GET_MEMBER(sn, 0)->v.lexeme = get_strp("stdin");
            AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,1)));
        } else {
            AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,2)));
            AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,3)));
        }
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

    case DEL_STMT:
        sn = newastnode(AST_DEL, NCH(pn)/2, pn->row, pn->col);
        for (ii=1, jj=0; jj<sn->size; ii+=2, jj++ ) {
            AST_SET_MEMBER(sn, jj, ast_from_pnode(CHILD(pn,ii)));
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
        sn = newastnode(AST_RAISE, NCH(pn)-1, pn->row, pn->col);
        if (NCH(pn) == 2) {
            AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,1)));
        }
        break;

    case IF_STMT:
        /*
         * Every IF ast has 3 members: test, true body and false body.
         * if ... elif ... elif ... else
         * is split'd into multiple tier of IF ast.
         */
        sn = newastnode(AST_IF, 3, pn->row, pn->col);
        AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,1))); // test
        AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,2))); // true
        if (NCH(pn) == 3) { // absent false body
            AST_SET_MEMBER(sn, 2, newastnode(AST_SEQ, 0, pn->row, pn->col));
        } else {
            ii = 3; // elif or else
            sn_left = sn;
            while (1) {
                if (CHILD(pn,ii)->type == ELIF) {
                    sn_temp = newastnode(AST_IF, 3, CHILD(pn,ii)->row,
                    CHILD(pn,ii)->col);
                    AST_SET_MEMBER(sn_left, 2, sn_temp);
                    AST_SET_MEMBER(sn_temp, 0, ast_from_pnode(CHILD(pn,ii+1)));
                    AST_SET_MEMBER(sn_temp, 1, ast_from_pnode(CHILD(pn,ii+2)));
                    ii += 3;
                    if (ii >= NCH(pn)) { // empty false body
                        AST_SET_MEMBER(sn_temp, 2,
                                newastnode(AST_SEQ, 0, pn->row, pn->col));
                        break;
                    }
                    sn_left = sn_temp;
                } else {
                    /*
                     * else must be the last clause
                     */
                    AST_SET_MEMBER(sn_left, 2, ast_from_pnode(CHILD(pn,ii+1)));
                    ii += 2;
                    break;
                }
            }
        }
        break;

    case WHILE_STMT:
        sn = newastnode(AST_WHILE, 2, pn->row, pn->col);
        AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn, 1))); // test
        AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn, 2))); // body
        break;

    case FOR_STMT:
        sn = newastnode(AST_FOR, 3, pn->row, pn->col);
        AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,1))); // counter
        AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,3))); // start, end, step
        AST_SET_MEMBER(sn, 2, ast_from_pnode(CHILD(pn,4)));
        break;

    case FUNCDEF:
        sn = newastnode(AST_FUNCDEF, 3, pn->row, pn->col);
        AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,1)));
        if (CHILD(pn,3)->type == ')') { // empty parameter list
            AST_SET_MEMBER(sn, 1,
                    newastnode(AST_LIST, 0, CHILD(pn,2)->row, CHILD(pn,2)->col));
            // body
            AST_SET_MEMBER(sn, 2, ast_from_pnode(CHILD(pn,4)));
        } else {
            // non empty parameter list is always consisted of
            // 3 members. see details in PARMLIST case.
            AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,3)));
            // body
            AST_SET_MEMBER(sn, 2, ast_from_pnode(CHILD(pn,5)));
        }
        break;

    case CLASSDEF:
        sn = newastnode(AST_CLASSDEF, 3, pn->row, pn->col);
        AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,1)));
        if (CHILD(pn,3)->type == ')') { // empty super list
            AST_SET_MEMBER(sn, 1,
                    newastnode(AST_IDENT, 0, CHILD(pn,2)->row, CHILD(pn,2)->col));
            AST_GET_MEMBER(sn, 1)->v.lexeme = get_strp("Object");
            // body
            AST_SET_MEMBER(sn, 2, ast_from_pnode(CHILD(pn,4)));
        } else {
            // non empty super list
            AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,3)));
            // body
            AST_SET_MEMBER(sn, 2, ast_from_pnode(CHILD(pn,5)));
        }
        break;

    case TRY_STMT:
        if (RCHILD(pn,0)->type == FINALLY_STMT) { // user supplied finally
            sn = newastnode(AST_TRY, NCH(pn) - 1, pn->row, pn->col);
            AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,1))); // try body
            for (ii = 2, jj = 1; ii < NCH(pn); ii++, jj++) // catch and finally
                AST_SET_MEMBER(sn, jj, ast_from_pnode(CHILD(pn,ii)));
        } else {
            sn = newastnode(AST_TRY, NCH(pn), pn->row, pn->col);
            AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,1))); // try body
            for (ii = 2, jj = 1; ii < NCH(pn); ii++, jj++) // catch
                AST_SET_MEMBER(sn, jj, ast_from_pnode(CHILD(pn,ii)));
            AST_SET_MEMBER(sn, jj, newastnode(AST_FINALLY, 0, pn->row, pn->col));
        }
        break;

    case CATCH_STMT:
        sn = newastnode(AST_CATCH, 3, pn->row, pn->col);
        AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,2)));
        AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,4)));
        AST_SET_MEMBER(sn, 2, ast_from_pnode(CHILD(pn,6)));
        break;

    case FINALLY_STMT:
        sn = newastnode(AST_FINALLY, 1, pn->row, pn->col);
        AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,1)));
        break;

    case SUITE:
        if (CHILD(pn,0)->type == SIMPLE_STMT) {
            sn = newastnode(AST_SEQ, 1, pn->row, pn->col);
            AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,0)));
        } else {
            sn = ast_from_pnode(CHILD(pn,0));
        }
        break;

    case STMT_BLOCK:
        sn = newastnode(AST_SEQ, NCH(pn) - 2, pn->row, pn->col);
        for (ii = 1, jj = 0; jj < sn->size; ii++, jj++) {
            AST_SET_MEMBER(sn, jj, ast_from_pnode(CHILD(pn,ii)));
        }
        break;

    case FOR_EXPR:
        sn = newastnode(AST_LIST, 3, pn->row, pn->col);
        AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,0)));
        AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,2)));
        if (NCH(pn) > 3) {
            AST_SET_MEMBER(sn, 2, ast_from_pnode(CHILD(pn,4)));
        } else {
            AST_SET_MEMBER(sn, 2, newastnode(AST_LITERAL, 0, pn->row, pn->col));
            AST_GET_MEMBER(sn, 2)->v.lexeme = get_strp("1");
        }
        break;

        /*
         * Binary operators
         */
    case R_EXPR:
    case R_TERM:
    case L_EXPR:
    case A_EXPR:
    case A_TERM:
    case POWER:
        if (NCH(pn) == 1) {
            sn = ast_from_pnode(CHILD(pn, 0));
        } else {
            for (ii = 1; ii < NCH(pn) - 1; ii += 2) {
                sn_left = sn;
                AST_TYPE_OF_BINOP(stype, pn, ii);
                sn = newastnode(stype, 2, CHILD(pn,ii)->row, CHILD(pn,ii)->col);
                if (sn_left == NULL)
                    AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,ii-1)));
                else
                    AST_SET_MEMBER(sn, 0, sn_left);
                AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,ii+1)));
            }
        }
        break;

        /*
         * Unary operators
         */
    case R_FACTOR:
    case FACTOR:
        if (NCH(pn) == 1) {
            sn = ast_from_pnode(CHILD(pn, 0));
        } else {
            AST_TYPE_OF_UNARYOP(stype, pn, 0);
            sn = newastnode(stype, 1, pn->row, pn->col);
            AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,1)));
        }
        break;

    case PRIMARY:
        if (NCH(pn) == 1) {
            sn = ast_from_pnode(CHILD(pn, 0));
        } else {
            sn = ast_from_pnode(CHILD(pn,0)); // the func/array/object
            pn = CHILD(pn, 1); // trailer
            ii = 0;
            while (ii < NCH(pn)) {
                sn_left = sn;
                AST_TYPE_OF_TRAILER(stype, pn, ii);
                sn = newastnode(stype, 2, CHILD(pn,ii)->row, CHILD(pn,ii)->col);
                AST_SET_MEMBER(sn, 0, sn_left);
                if (stype == AST_CALL && CHILD(pn,ii+1)->type == ')') { // no argument func
                    AST_SET_MEMBER(sn, 1,
                            newastnode(AST_LIST, 0, CHILD(pn,ii+2)->row, CHILD(pn,ii+2)->col));
                    ii += 2;
                } else {
                    AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,ii+1)));
                    if (stype == AST_FIELD)
                        ii += 2;
                    else
                        ii += 3;
                }
            }
        }
        break;

    case ATOM:
        if (NCH(pn) == 1)
            sn = ast_from_pnode(CHILD(pn, 0));
        else { // ( expr )
            sn = ast_from_pnode(CHILD(pn, 1));
        }
        break;

    case EXPR_LIST:
        sn = newastnode(AST_LIST, NCH(pn) / 2 + 1, pn->row, pn->col);
        for (ii = jj = 0; jj < sn->size; ii += 2, jj++) {
            AST_SET_MEMBER(sn, jj, ast_from_pnode(CHILD(pn,ii)));
        }
        break;

    case PARMLIST:
        /*
         * Always has 3 members and they are regular parameters (positional
         * and keyword), extra parameter and extra keywords. If they
         * are not provided by user code, they will be set as empty.
         */
        sn = newastnode(AST_LIST, 3, pn->row, pn->col);
        if (CHILD(pn,0)->type == DSTAR) { // only extra keywords **c
            AST_SET_MEMBER(sn, 0, newastnode(AST_LIST,0,pn->row,pn->col));
            AST_SET_MEMBER(sn, 1, newastnode(AST_EXTRAP, 0, pn->row, pn->col));
            sn_temp = newastnode(AST_EXTRAK, 1, CHILD(pn,0)->row,
                    CHILD(pn,0)->col);
            AST_SET_MEMBER(sn_temp, 0, ast_from_pnode(CHILD(pn,1)));
            AST_SET_MEMBER(sn, 2, sn_temp);
        } else if (CHILD(pn,0)->type == '*') { // no regular params
            AST_SET_MEMBER(sn, 0, newastnode(AST_LIST,0,pn->row,pn->col));
            if (NCH(pn) > 2) { // *b, **c
                sn_temp = newastnode(AST_EXTRAP, 1, CHILD(pn,0)->row,
                CHILD(pn,0)->col); // *b
                AST_SET_MEMBER(sn_temp, 0, ast_from_pnode(CHILD(pn,1)));
                AST_SET_MEMBER(sn, 1, sn_temp);
                sn_temp = newastnode(AST_EXTRAK, 1, CHILD(pn,3)->row,
                CHILD(pn,3)->col); // **c
                AST_SET_MEMBER(sn_temp, 0, ast_from_pnode(CHILD(pn,4)));
                AST_SET_MEMBER(sn, 2, sn_temp);
            } else {
                sn_temp = newastnode(AST_EXTRAP, 1, CHILD(pn,0)->row,
                CHILD(pn,0)->col); // *b
                AST_SET_MEMBER(sn_temp, 0, ast_from_pnode(CHILD(pn,1)));
                AST_SET_MEMBER(sn, 1, sn_temp);
                AST_SET_MEMBER(sn, 2,
                        newastnode(AST_EXTRAK, 0, pn->row, pn->col));
            }
        } else { // start with regular params
            if (NCH(pn) == 1) { // a only
                AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,0)));
                AST_SET_MEMBER(sn, 1,
                        newastnode(AST_EXTRAP, 0, pn->row, pn->col));
                AST_SET_MEMBER(sn, 2,
                        newastnode(AST_EXTRAK, 0, pn->row, pn->col));
            } else if (NCH(pn) > 3) { // a, *b, **c
                AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,0))); // a
                sn_temp = newastnode(AST_EXTRAP, 1, CHILD(pn,1)->row,
                CHILD(pn,1)->col); // *b
                AST_SET_MEMBER(sn_temp, 0, ast_from_pnode(CHILD(pn,2)));
                AST_SET_MEMBER(sn, 1, sn_temp);
                sn_temp = newastnode(AST_EXTRAK, 1, CHILD(pn,4)->row,
                CHILD(pn,4)->col);
                AST_SET_MEMBER(sn_temp, 0, ast_from_pnode(CHILD(pn,5)));
                AST_SET_MEMBER(sn, 2, sn_temp);
            } else { //
                AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,0))); // a
                if (CHILD(pn,1)->type == '*') { // *b
                    sn_temp = newastnode(AST_EXTRAP, 1, CHILD(pn,1)->row,
                    CHILD(pn,1)->col); // *b
                    AST_SET_MEMBER(sn_temp, 0, ast_from_pnode(CHILD(pn,2)));
                    AST_SET_MEMBER(sn, 1, sn_temp);
                    AST_SET_MEMBER(sn, 2,
                            newastnode(AST_EXTRAK, 0, pn->row, pn->col));
                } else { // **c
                    AST_SET_MEMBER(sn, 1,
                            newastnode(AST_EXTRAP, 0, pn->row, pn->col));
                    sn_temp = newastnode(AST_EXTRAK, 1, CHILD(pn,1)->row,
                    CHILD(pn,1)->col); // *b
                    AST_SET_MEMBER(sn_temp, 0, ast_from_pnode(CHILD(pn,2)));
                    AST_SET_MEMBER(sn, 2, sn_temp);
                }
            }
        }
        break;

    case OPARM_LIST:
        if (RCHILD(pn,0)->type == ',') {
            sn = newastnode(AST_LIST, NCH(pn) / 2, pn->row, pn->col);
        } else {
            sn = newastnode(AST_LIST, NCH(pn) / 2 + 1, pn->row, pn->col);
        }
        for (ii = jj = 0; jj < sn->size; ii += 2, jj++) {
            AST_SET_MEMBER(sn, jj, ast_from_pnode(CHILD(pn,ii)));
        }
        break;

    case OPARM:
        sn = ast_from_pnode(CHILD(pn,0));
        break;

    case KVPAIR:
        sn = newastnode(AST_KVPAIR, 2, pn->row, pn->col);
        AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,0)));
        AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,2)));
        break;

    case ARGLIST:
        sn = newastnode(AST_LIST, NCH(pn) / 2 + 1, pn->row, pn->col);
        for (ii = jj = 0; jj < sn->size; ii += 2, jj++) {
            AST_SET_MEMBER(sn, jj, ast_from_pnode(CHILD(pn,ii)));
        }
        break;

    case OARG:
        sn = ast_from_pnode(CHILD(pn,0));
        break;

    case SUBSCRIPTION:
        sn = ast_from_pnode(CHILD(pn,0));
        break;

    case SINGLEIDX:
        sn = ast_from_pnode(CHILD(pn,0));
        break;

    case IDXRANGE:
        sn = newastnode(AST_LIST, 3, pn->row, pn->col);
        // start
        if (CHILD(pn,0)->type == ':') {
            AST_SET_MEMBER(sn, 0,
                    newastnode(AST_LITERAL, 0, CHILD(pn,0)->row, CHILD(pn,0)->col));
            AST_GET_MEMBER(sn, 0)->v.lexeme = get_strp("0");
            ii = 1;
        } else {
            AST_SET_MEMBER(sn, 0, ast_from_pnode(CHILD(pn,0)));
            ii = 2;
        }
        // end
        if (ii >= NCH(pn)) {
            AST_SET_MEMBER(sn, 1,
                    newastnode(AST_LITERAL, 0, CHILD(pn,0)->row, CHILD(pn,0)->col));
            AST_GET_MEMBER(sn, 1)->v.lexeme = get_strp("-1");
            // step
            AST_SET_MEMBER(sn, 2,
                    newastnode(AST_LITERAL, 0, CHILD(pn,0)->row, CHILD(pn,0)->col));
            AST_GET_MEMBER(sn, 2)->v.lexeme = get_strp("1");
        } else {
            // end
            if (CHILD(pn,ii)->type == ':') {
                AST_SET_MEMBER(sn, 1,
                        newastnode(AST_LITERAL, 0, CHILD(pn,0)->row, CHILD(pn,0)->col));
                AST_GET_MEMBER(sn, 1)->v.lexeme = get_strp("-1");
                ii += 1;
            } else {
                AST_SET_MEMBER(sn, 1, ast_from_pnode(CHILD(pn,ii)));
                ii += 2;
            }
            // step
            if (ii >= NCH(pn)) {
                AST_SET_MEMBER(sn, 2,
                        newastnode(AST_LITERAL, 0, CHILD(pn,0)->row, CHILD(pn,0)->col));
                AST_GET_MEMBER(sn, 2)->v.lexeme = get_strp("1");
            } else {
                AST_SET_MEMBER(sn, 2, ast_from_pnode(CHILD(pn,ii)));
            }
        }
        break;

    case IDXLIST:
        sn = newastnode(AST_LIST, NCH(pn) / 2 + 1, pn->row, pn->col);
        for (ii = jj = 0; jj < sn->size; ii += 2, jj++) {
            AST_SET_MEMBER(sn, jj, ast_from_pnode(CHILD(pn,ii)));
        }
        break;

    case '*':
        sn = newastnode(AST_SYMBOL, 0, pn->row, pn->col);
        AST_SET_SYMBOL(sn, '*');
        break;

    case IDENT:
        sn = newastnode(AST_IDENT, 0, pn->row, pn->col);
        AST_SET_LEXEME(sn, pn->lexeme);
        break;

    case INTEGER:
    case FLOAT:
    case STRING:
        sn = newastnode(AST_LITERAL, 0, pn->row, pn->col);
        AST_SET_LEXEME(sn, pn->lexeme);
        break;

    case NUL:
        sn = newastnode(AST_LITERAL, 0, pn->row, pn->col);
        break;

    default:
        fatal("unknown parse node when constructing AST");
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
