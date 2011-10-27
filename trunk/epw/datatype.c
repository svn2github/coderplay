/*
 * =====================================================================================
 *
 *       Filename:  datatype.c
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  10/27/2011 10:51:58 PM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  ywangd (sonickenking), ywangd@gmail.com
 *        Company:  
 *
 * =====================================================================================
 */
#include <stdio.h>
#include <stdlib.h>
#include "symtab.h"
#include "datatype.h"
#include "epw.h"

dataobj_t *
create_dataobj (datatypeEnum type, void *data, int gcdata)
{
    dataobj_t *newdo;
    newdo = (dataobj_t *) malloc (sizeof (dataobj_t));
    newdo->dataType = type;
    newdo->data = data;
    newdo->gcdata = gcdata;
    return newdo;
}

void
delete_dataobj (dataobj_t * dobj)
{
    if (!dobj)
        return;
    /* free the data pointer if specified */
    if (dobj->gcdata == FREE_DATA_PTR_WHEN_DELETE && dobj->data) 
        free (dobj->data);
    free (dobj);
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

dataobj_t *
get_data_from_symbol(symbol_t *sym) {
    dataobj_t *dobj = NULL;
    switch (sym->symType) {
        case SYM_NUM:
            dobj = create_dataobj(DT_NUM, sym->value, KEEP_DATA_PTR_WHEN_DELETE);
            break;
        case SYM_STR:
            dobj = create_dataobj(DT_STR, sym->value, KEEP_DATA_PTR_WHEN_DELETE);
            break;
        default:
            fprintf(stderr, "Unknown symbol type\n");
            break;
    }
    return dobj;
}

dataobj_t *
create_dataobj_zero ()
{
    double *data = (double *)malloc(sizeof(double));
    *data = 0.0;
    return  create_dataobj(DT_NUM, data, FREE_DATA_PTR_WHEN_DELETE);
}

