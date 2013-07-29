/*
 * hashobject.h
 *
 *  Created on: 28/07/2013
 *      Author: ywangd@gmail.com
 */

#ifndef HASHOBJECT_H_
#define HASHOBJECT_H_

extern EmTypeObject Hashtype;
typedef struct _hashobject EmHashObject;

EmHashObject* hashobject_new(unsigned int size);

void hashobject_free(EmHashObject* ht);

EmHashObject* hashobject_insert(EmHashObject* ht, EmObject *key, EmObject *val);

void hashobject_delete(EmHashObject* ht, EmObject *key);

Word* hashobject_lookup(EmHashObject* ht, EmObject *key);

EmHashObject* hashobject_rehash(EmHashObject* ht);

void hashobject_dump(EmHashObject* ht);

#endif /* HASHOBJECT_H_ */
