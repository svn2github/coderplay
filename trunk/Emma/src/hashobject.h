/*
 * hashobject.h
 *
 *  Created on: 28/07/2013
 *      Author: ywangd@gmail.com
 */

#ifndef HASHOBJECT_H_
#define HASHOBJECT_H_

#define is_EmHashObject(ob) ((ob)->type == &Hashtype)
#define DEFAULT_HASH_SIZE       13u

typedef struct {
    EmObject *key;
    EmObject *val;
} EmHashEntry;

typedef struct _hashobject {
    OB_HEAD; // nitems included
    unsigned int size; // size of the hash including unused spots
    EmHashEntry **table; // the entry array
} EmHashObject;

extern EmTypeObject Hashtype;

EmObject *newhashobject();
EmObject *newhashobject_from_size(unsigned int size);
void hashobject_free(EmObject *ho);
void hashobject_print(EmObject *ho, FILE *fp);

EmObject* hashobject_lookup(EmObject *ho, EmObject *key);
EmObject* hashobject_insert(EmObject *ho, EmObject *key, EmObject *val);
int hashobject_delete(EmObject *ho, EmObject *key);

EmObject *hashobject_lookup_by_string(EmObject *ho, char *key);
EmObject *hashobject_insert_by_string(EmObject *ho, char *key, EmObject *val);
int hashobject_delete_by_string(EmObject *ho, char *key);

#endif /* HASHOBJECT_H_ */
