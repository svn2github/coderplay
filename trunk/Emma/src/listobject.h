/*
 * listobject.h
 *
 *  Created on: 01/08/2013
 *      Author: ywangd
 */

#ifndef LISTOBJECT_H_
#define LISTOBJECT_H_

#define is_EmListObject(ob) ((ob)->type == &Listtype)
#define DEFAULT_LIST_SIZE       16u


typedef struct _listobject {
    OB_HEAD;
    unsigned int size;
    EmObject **list;
} EmListObject;

extern EmTypeObject Listtype;

EmObject *newlistobject(unsigned int size);
void listobject_free(EmObject *ob);
void listobject_print(EmObject *ob, FILE *fp);

EmObject *listobject_get(EmObject *ob, int idx);
EmObject *listobject_set(EmObject *ob, int idx);
EmObject *listobject_append(EmObject *ob, EmObject u);
EmObject *listobject_delete(EmObject *ob, int idx);
EmObject *listobject_pop(EmObject *ob);
EmObject *listobject_shift(EmObject *ob);


#endif /* LISTOBJECT_H_ */
