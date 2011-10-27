#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "epw.h"

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

/* hash a string */
static unsigned
hash(char *name)
{
  unsigned int hash = 0;
  unsigned c;
  while(c = *name++) hash = hash*9 ^ c;
  return hash;
}

symbol_t *
lookup(char *name)
{
  symbol_t *sp = &symtab[hash(name)%NMAX_SYMBOL];
  int scount = NMAX_SYMBOL;       /* how many have we looked at */

  while(--scount >= 0) {
    if(sp->name && !strcmp(sp->name, name)) { return sp; }

    if(!sp->name) {     /* new entry */
      sp->name = strdup(name);
      sp->value = 0;
      sp->udf = NULL;
      sp->paralist = NULL;
      return sp;
    }

    if(++sp >= symtab+NMAX_SYMBOL) sp = symtab; /* try the next entry */
  }
  fprintf(stderr, "Internal error: symbol table overflow\n");
  exit(EXIT_FAILURE); /* tried them all, table is full */
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
  pnode->nodeType = NUM;
  pnode->val = val;
  return (tnode_t *) pnode;
}

tnode_t *
new_strnode (char *val)
{
  strnode_t *pnode;
  pnode = (strnode_t *) safe_malloc (sizeof (strnode_t));
  pnode->nodeType = STR;
  pnode->val = val;
  return (tnode_t *) pnode;
}

tnode_t *
new_symnode (symbol_t *sym)
{
  symnode_t *pnode;
  pnode = (symnode_t *) safe_malloc (sizeof (symnode_t));
  pnode->nodeType = SYM;
  pnode->sym = sym;
  return (tnode_t *) pnode;
}

tnode_t *
new_asnnode (symbol_t *l, tnode_t *r)
{
  asnnode_t * pnode;
  pnode = (asnnode_t *) safe_malloc(sizeof (asnnode_t));
  pnode->nodeType = ASN;
  pnode->l = l;
  pnode->r = r;
  return (tnode_t *) pnode;
}


void
delete_node (tnode_t * pnode)
{
  if (!pnode)
    return;

  switch (pnode->nodeType)
    {
    case NUM:
      break;
    case STR:
      free (((strnode_t *)pnode)->val);
      break;
    case SYM: /* symtab is not an array and does not need to be freed */
      break;
    case ASN:
      delete_node (pnode->r);
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


