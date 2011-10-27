#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "syntree.h"

void *
safe_malloc (size_t size)
{
    void *new;
    new = malloc (size);
    if (!new)
      {
          fprintf (stderr, "Memory allocation failed! Aborting!\n");
          exit (EXIT_FAILURE);
      }
    return (new);
}

tnode_t *
new_tnode (int nodeType, void *data, tnode_t * l, tnode_t * r)
{
    tnode_t *pnode;
    pnode = (tnode_t *) safe_malloc (sizeof (tnode_t));
    pnode->nodeType = nodeType;
    pnode->data = data;
    pnode->l = l;
    pnode->r = r;
    return pnode;
}

void
delete_node (tnode_t * pnode)
{
    if (!pnode)
        return;

    switch (pnode->nodeType)
      {
      case NUM:
      case STR:
          free(pnode->data);
          break;
      case SYM:
          break;
      case ASN:
      case PRN:
      case ADD:
      case SUB:
      case MUL:
      case DIV:
      case MOD:
          break;
      default:
          fprintf (stderr, "Internal error: free bad node %c\n",
                   pnode->nodeType);
          break;
      }
    /* free the child nodes */
    delete_node (pnode->l);
    delete_node (pnode->r);
    /* free the node itself */
    free (pnode);
}
