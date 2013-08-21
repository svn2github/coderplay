/*
 * listobject.h
 *
 *  Created on: 01/08/2013
 *      Author: ywangd
 */

#ifndef LISTOBJECT_H_
#define LISTOBJECT_H_

#define is_EmListObject(ob) ((ob)->type == &Listtype)
#define DEFAULT_LIST_SIZE       1u


typedef struct _listobject {
    OB_HEAD;
    unsigned int size;
    EmObject **list;
} EmListObject;

extern EmTypeObject Listtype;

EmObject *newlistobject(unsigned int size);
EmObject *newlistobject_of_null(unsigned int size);
void listobject_free(EmObject *ob);
void listobject_print(EmObject *ob, FILE *fp);

EmObject *listobject_get(EmObject *ob, int idx);
EmObject *listobject_slice(EmObject *ob, int start, int end, int step);
EmObject *listobject_slice_by_list(EmObject *ob, EmObject *slice);
EmObject *listobject_idxlist(EmObject *ob, EmObject *idxlist);

int listobject_set_slice(EmObject *ob, EmObject *slice, EmObject *val);
int listobject_set_idxlist(EmObject *ob, EmObject *idxlist, EmObject *val);

int listobject_set(EmObject *ob, int idx, EmObject *val);
int listobject_append(EmObject *ob, EmObject *val);
int listobject_insert(EmObject *ob, int idx, EmObject *val);
EmObject *listobject_delete(EmObject *ob, int idx);
EmObject *listobject_pop(EmObject *ob);
EmObject *listobject_shift(EmObject *ob);
int listobject_index(EmObject *ob, EmObject *val);


#endif /* LISTOBJECT_H_ */
