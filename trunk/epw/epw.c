#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symtab.h"
#include "syntree.h"
#include "epw.h"

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
    case NUM:
      return ((numnode_t *) pnode)->val;
      break;
    case STR:
      printf("= %s\n", ((strnode_t *) pnode)->val);
      return 0;
      break;
    case SYM:
      printf("= name %s\n", ((symnode_t *) pnode)->sym->name);
      return 0;
      break;
    case ASN:
      return ((asnnode_t *)pnode)->l->value = eval(pnode->r);
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


