#include <stdio.h>
#include <stdlib.h>
#include "ipc.h"

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
new_tnode (int nodeType, tnode_t * l, tnode_t * r)
{
  tnode_t *pnode;
  pnode = (tnode_t *) safe_malloc (sizeof (tnode_t));
  pnode->nodeType = nodeType;
  pnode->l = l;
  pnode->r = r;
  return pnode;
}

tnode_t *
new_numnode (double val)
{
  numnode_t *pnode;
  pnode = (numnode_t *) safe_malloc (sizeof (numnode_t));
  pnode->nodeType = NUMBER_CONSTANT;
  pnode->val = val;
  return (tnode_t *) pnode;
}

tnode_t *
new_strnode (char *val)
{
  strnode_t *pnode;
  pnode = (strnode_t *) safe_malloc (sizeof (strnode_t));
  pnode->nodeType = STRING_LITERAL;
  pnode->val = val;
  return (tnode_t *) pnode;
}


void
delete_node (tnode_t * pnode)
{
  if (!pnode)
    return;

  switch (pnode->nodeType)
    {
    case NUMBER_CONSTANT:
      break;
    case STRING_LITERAL:
      free (((strnode_t *)pnode)->val);
      break;
    case PRN:
    case ADD:
    case SUB:
    case MUL:
    case DIV:
    case MOD:
      delete_node (pnode->l);
      delete_node (pnode->r);
      break;
    default:
      fprintf (stderr, "Internal error: free bad node %c\n", pnode->nodeType);
      break;
    }
  free (pnode);
}

double 
eval (tnode_t * pnode)
{
  if (!pnode)
    {
      fprintf (stderr, "Internal error: cannot evaluate null node");
      return;
    }

  switch (pnode->nodeType)
    {
    case NUMBER_CONSTANT:
      return ((numnode_t *) pnode)->val;
      break;
    case STRING_LITERAL:
      printf("= %s\n", ((strnode_t *) pnode)->val);
      return 0;
      break;
    case ADD:
      return eval (pnode->l) + eval (pnode->r);
      break;
    case SUB:
      return eval (pnode->l) - eval (pnode->r);
      break;
    case MUL:
      return eval (pnode->l) * eval (pnode->r);
      break;
    case DIV:
      return eval (pnode->l) / eval (pnode->r);
      break;
    case MOD:
      printf("MOD\n");
      return 0;
      //eval (pnode->l) % eval (pnode->r);
      break;
    case PRN:
      printf("= print %f\n", eval (pnode->l));
      PRINTLN;
      return 0;
      break;
    default:
      fprintf (stderr, "Internal error: unknown node type");
    }
}


