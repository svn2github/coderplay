#include <stdio.h>
#include "ipc.h"

    void *
safe_malloc(size_t size)
{
    void *new;
    new = malloc(size);
    if (!new) {
        fprintf(stderr, "Memory allocation failed! Aborting!\n");
        exit(EXIT_FAILURE);
    }
    return (new);
}

    char           *
safe_strdup(const char *str)
{
    char           *newstr;
    newstr = (char *) safe_malloc(strlen(str) + 1);
    strcpy(newstr, str);
    return (newstr);
}   



    tnode_t *
new_tnode(int nodeType, tnode_t *l, tnode_t *r)
{
    tnode_t *pnode = safe_malloc(sizeof(tnode_t));
    pnode->nodeType = nodeType;
    pnode->l = l;
    pnode->r = r;
    return pnode;
}

    tnode_t*
new_numnode(double val)
{
    numnode_t *pnode = safe_malloc(sizeof(numnode_t));
    pnode->nodeType = NUMBER_CONSTANT;
    pnode->val = val;
    return (tnode_t *)pnode;
}

    tnode_t*
new_strnode(char *val)
{
    strnode_t *pnode = safe_malloc(sizeof(strnode_t));
    pnode->nodeType = STRING_LITERAL;
    pnode-val = val;
    return (tnode_t *)pnode;
}


void
delete_node(tnode_t *pnode) {
    if (!pnode) return;

    swtich(pnode->nodeType) {
        case NUMBER_CONSTANT: 
            break;
        case STRING_LITERAL:
            free(pnode->val);
            break;
        case PRN:
        case ADD: case SUB: case MUL: case DIV: case MOD:
            delete_node(pnode->l);
            delete_node(pnode->r);
        default:
            fprintf(stderr, "Internal error: free bad node %c\n", pnode->nodeType);
    }
    free(pnode);
}

void
eval(tnode_t *pnode) {
    if (!pnode) {
        fprintf(stderr, "Internal error: cannot evaluate null node");
    }

    switch (pnode->nodeType) {
        case NUMBER_CONSTANT: 
            printf("= %f\n", ((numnode_t *)pnode)->val);
            break;
        case STRING_LITERAL:
            printf("= %s\n", ((strnode_t *)pnode)->val);
            break;
        case ADD: 
            printf("= %f\n", eval(pnode->l) + eval(pnode->r));
            break;
        case SUB: 
            printf("= %f\n", eval(pnode->l) - eval(pnode->r));
            break;
        case MUL: 
            printf("= %f\n", eval(pnode->l) * eval(pnode->r));
            break;
        case DIV: 
            printf("= %f\n", eval(pnode->l) / eval(pnode->r));
            break;
        case MOD: 
            printf("= %f\n", eval(pnode->l) % eval(pnode->r));
            break;
        case PRN:
            printf("= print %s\n", eval(pnode->l));
            break;
    }
}




