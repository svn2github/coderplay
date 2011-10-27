#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symtab.h"
#include "syntree.h"
#include "datatype.h"
#include "epw.h"

dataobj_t *
eval (tnode_t * pnode)
{
    if (!pnode)
      {
          fprintf (stderr, "Internal error: cannot evaluate null node\n");
          return;
      }

    dataobj_t *dobj = NULL;
    /* temporary data object pointer */
    dataobj_t *to1 = NULL, *to2 = NULL;

    switch (pnode->nodeType)
      {
      case NUM:
          dobj = create_dataobj (DT_NUM, pnode->data, FREE_DATA_PTR_WHEN_DELETE);
          pnode->data = NULL;
          break;
      case STR:
          dobj = create_dataobj (DT_STR, pnode->data, FREE_DATA_PTR_WHEN_DELETE);
          pnode->data = NULL;
          break;
      case SYM:
          dobj = create_dataobj (DT_SYM, pnode->data, KEEP_DATA_PTR_WHEN_DELETE);
          pnode->data = NULL;
          break;
      case ASN:
          dobj = eval (pnode->l);
          to2 = eval (pnode->r);
          if (dobj->dataType != DT_SYM)
            {
                fprintf (stderr, "cannot assign to an expression\n");
                break;
            }
          /* clear the contents of the symbol for new value */
          reset_symbol((symbol_t *)dobj->data);
          ((symbol_t *)dobj->data)->value = to2->data;
          to2->data = NULL;
          if (to2->dataType == DT_NUM)
              ((symbol_t *)dobj->data)->symType = SYM_NUM;
          else if (to2->dataType == DT_STR)
              ((symbol_t *)dobj->data)->symType = SYM_STR;
          break;
      case ADD:
      case SUB:
      case MUL:
      case DIV:
      case MOD:
          to1 = eval (pnode->l);
          to2 = eval (pnode->r);
          dobj = op_arithmetic(to1, to2, pnode->nodeType);
          break;
      case PRN:
          to1 = eval (pnode->l);
          if (to1) print_dataobj(to1); 
          break;
      default:
          fprintf (stderr, "Internal error: unknown node type\n");
      }

    delete_dataobj (to1);
    delete_dataobj (to2);
    return dobj;
}

dataobj_t * 
op_arithmetic(dataobj_t *d1, dataobj_t *d2, int operation)
{
    dataobj_t *dobj = NULL;
    dataobj_t *o1=NULL, *o2=NULL;
    int freeo1=0,  freeo2=0;
    datatypeEnum dtype;

    double *dres = NULL; 
    char *sres = NULL;
    int l1, l2;

    if (d1->dataType == DT_SYM) {
        o1 = get_data_from_symbol((symbol_t *)d1->data);
        freeo1 = 1;
    } else {
        o1 = d1;
    }
    if (d2->dataType == DT_SYM) {
        o2 =get_data_from_symbol((symbol_t *)d2->data);
        freeo2 = 1;
    } else {
        o2 = d2;
    }

    dtype = o1->dataType;
    if (dtype != o2->dataType) {
        fprintf(stderr,  "operands are different type\n");
        if (freeo1) delete_dataobj(o1);
        if (freeo2) delete_dataobj(o2);
        return NULL;
    }

    switch (dtype) {
        case DT_NUM:
            switch (operation) {
                case ADD:
                    dres = (double *)malloc(sizeof(double));
                    *dres = *(double *) o1->data + *(double *) o2->data;
                    dobj = create_dataobj (DT_NUM, dres, FREE_DATA_PTR_WHEN_DELETE);
                    break;
                case SUB:
                    dres = (double *)malloc(sizeof(double));
                    *dres = *(double *) o1->data - *(double *) o2->data;
                    dobj = create_dataobj (DT_NUM, dres, FREE_DATA_PTR_WHEN_DELETE);
                    break;
                case MUL:
                    dres = (double *)malloc(sizeof(double));
                    *dres = *(double *) o1->data * *(double *) o2->data;
                    dobj = create_dataobj (DT_NUM, dres, FREE_DATA_PTR_WHEN_DELETE);
                    break;
                case DIV:
                    dres = (double *)malloc(sizeof(double));
                    *dres = *(double *) o1->data / *(double *) o2->data;
                    dobj = create_dataobj (DT_NUM, dres, FREE_DATA_PTR_WHEN_DELETE);
                    break;
                default:
                    fprintf(stderr, "operation not supported\n");
                    break;
            }
            break;

        case DT_STR:
            l1 = strlen((char *)o1->data);
            l2 = strlen((char *)o2->data);
            switch (operation) {
                case ADD:
                    sres = (char *) malloc(sizeof(char)*(l1+l2+1));
                    strcpy(sres, (char *)o1->data);
                    strcpy(sres+l1, (char *)o2->data);
                    dobj = create_dataobj (DT_STR, sres, FREE_DATA_PTR_WHEN_DELETE);
                    break;
                default:
                    fprintf(stderr, "operation not supported\n");
                    break;
            }
            break;
        default:
            fprintf(stderr, "Unknown data type\n");
            break;
    }
    if (freeo1) delete_dataobj(o1);
    if (freeo2) delete_dataobj(o2);
    return dobj;
}

int main(int argc, char **argv)
{
    if (argc > 1) {
        if (!(yyin = fopen(argv[1], "r"))) {
            perror(argv[1]);
        }
    } else {
        printf("Emma Peiran Wang says hi\n");
        printf("[%d]> ", yylineno);
    }
    yyparse();

    /* release the resources used by the symbol table */
    delete_symtab();

    return 0;
}


