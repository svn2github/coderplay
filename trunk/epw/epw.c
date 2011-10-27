#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symtab.h"
#include "syntree.h"
#include "epw.h"

dataobj_t *
create_dataobj (datatypeEnum type, void *data)
{
    dataobj_t *newdo;
    newdo = (dataobj_t *) malloc (sizeof (dataobj_t));
    newdo->dataType = type;
    newdo->data = data;
    return newdo;
}

void
delete_dataobj (dataobj_t * dobj)
{
    if (!dobj)
        return;
    if (dobj->data && dobj->dataType != DT_SYM)
        free (dobj->data);
    free (dobj);
}

dataobj_t *
eval (tnode_t * pnode)
{
    if (!pnode)
      {
          fprintf (stderr, "Internal error: cannot evaluate null node\n");
          return;
      }

    dataobj_t *dobj = NULL;
    dataobj_t *to1 = NULL, *to2 = NULL;
    double *res;

    switch (pnode->nodeType)
      {
      case NUM:
          dobj = create_dataobj (DT_NUM, pnode->data);
          pnode->data = NULL;
          break;
      case STR:
          dobj = create_dataobj (DT_STR, pnode->data);
          pnode->data = NULL;
          break;
      case SYM:
          dobj = create_dataobj (DT_SYM, pnode->data);
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
          ((symbol_t *)dobj->data)->value = to2->data;
          if (to2->dataType == DT_NUM)
              ((symbol_t *)dobj->data)->symType = SYM_NUM;
          else if (to2->dataType == DT_STR)
              ((symbol_t *)dobj->data)->symType = SYM_STR;
          break;
      case ADD:
          to1 = eval (pnode->l);
          to2 = eval (pnode->r);
          res = (double *) malloc (sizeof (double));
          *res = *(double *) to1->data + *(double *) to2->data;
          dobj = create_dataobj (DT_NUM, res);
          break;
      case SUB:
          to1 = eval (pnode->l);
          to2 = eval (pnode->r);
          res = (double *) malloc (sizeof (double));
          *res = *(double *) to1->data - *(double *) to2->data;
          dobj = create_dataobj (DT_NUM, res);
          break;
      case MUL:
          to1 = eval (pnode->l);
          to2 = eval (pnode->r);
          res = (double *) malloc (sizeof (double));
          *res = *(double *) to1->data * *(double *) to2->data;
          dobj = create_dataobj (DT_NUM, res);
          break;
      case DIV:
          to1 = eval (pnode->l);
          to2 = eval (pnode->r);
          res = (double *) malloc (sizeof (double));
          *res = *(double *) to1->data / *(double *) to2->data;
          dobj = create_dataobj (DT_NUM, res);
          break;
      case MOD:
          to1 = eval (pnode->l);
          to2 = eval (pnode->r);
          res = (double *) malloc (sizeof (double));
          *res =
              ((int) *(double *) to1->data) / ((int) *(double *) to2->data);
          dobj = create_dataobj (DT_NUM, res);
          break;
      case PRN:
          to1 = eval (pnode->l);
          print_dataobj(to1);
          break;
      default:
          fprintf (stderr, "Internal error: unknown node type\n");
      }

    //delete_dataobj (to1);
    //delete_dataobj (to2);
    return dobj;
}

void
print_dataobj (dataobj_t * dobj)
{
    switch (dobj->dataType)
      {
      case DT_NUM:
          printf ("%g\n", *(double *) dobj->data);
          break;
      case DT_STR:
          printf ("%s\n", (char *) dobj->data);
          break;
      case DT_SYM:
          printf ("%s = ", ((symbol_t *) dobj->data)->name);
          switch (((symbol_t *) dobj->data)->symType)
            {
            case SYM_NUM:
                printf ("%g\n", *(double *) (((symbol_t *) dobj->data)->value));
                break;
            case SYM_STR:
                printf ("%s\n", (char *) (((symbol_t *) dobj->data)->value));
                break;
            default:
                fprintf (stderr, "Internal error: unknown symbol type\n");
                break;
            }
          break;
      case DT_NUL:
          printf ("NULL\n");
          break;
      default:
          fprintf (stderr, "Internal error: unknown data type\n");
          break;
      }
    PRINTLN;
}
