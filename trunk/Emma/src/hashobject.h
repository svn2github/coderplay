/*
 * hashobject.h
 *
 *  Created on: 28/07/2013
 *      Author: ywangd@gmail.com
 */

#ifndef HASHOBJECT_H_
#define HASHOBJECT_H_

#define DEFAULT_HASH_SIZE       13u

extern EmTypeObject Hashtype;
typedef struct _hashobject EmHashObject;

EmHashObject* newhashobject();
void hashobject_free(EmHashObject *ht);
void hashobject_print(EmHashObject *ht, FILE *fp);

EmObject* hashobject_lookup(EmHashObject *ht, EmObject *key);
EmHashObject* hashobject_insert(EmHashObject *ht, EmObject *key, EmObject *val);
EmHashObject* hashobject_rehash(EmHashObject *ht);
int hashobject_delete(EmHashObject *ht, EmObject *key);

EmObject *hashobject_lookup_by_string(EmHashObject *ht, char *key);
EmHashObject *hashobject_insert_by_string(EmHashObject *ht, char *key, EmObject *val);
int hashobject_delete_by_string(EmHashObject *ht, char *key);

#endif /* HASHOBJECT_H_ */
