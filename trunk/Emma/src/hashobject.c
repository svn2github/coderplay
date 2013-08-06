#include "allobject.h"

/*
 * TODO:
 * 1. May save hash value of the key, so comparison and especially rehash
 *    can be faster.
 * 2. Use dummy entry so I don't have to dealloc when deleting keys.
 * 3. Some records of the keys, so I don't have to loop all slots to find
 *    filled entries.
 */

static unsigned int prime_numbers[] = {
    3, 7, 13, 31, 61, 127, 251, 509, 1021, 2017, 4093,
    5987, 9551, 15683, 19609, 31397, // 59999,
};

static unsigned int npnumbers = sizeof(prime_numbers) / sizeof(unsigned int);

unsigned int ht_getprime(unsigned int size) {
    int ii;
    for (ii=0; ii< npnumbers; ii++) {
        if (prime_numbers[ii] >= size)
            return prime_numbers[ii];
    }
    return 0;
}

EmObject *
newhashobject_from_size(unsigned int size_req) {
    EmHashObject *ht;
    unsigned int size;

    if (!(size = ht_getprime(size_req)))
        return log_error(MEMORY_ERROR, "hash table size overflow");

    if ((ht = NEWOBJ(EmHashObject, &Hashtype)) == NULL)
        return NULL;

    ht->size = size;
    ht->nitems = 0;

    if ((ht->table = (EmHashEntry **) calloc(ht->size, sizeof(EmHashEntry *)))
            == NULL) {
        DEL(ht);
        return log_error(MEMORY_ERROR, "not enough memory for hashtable");
    }
    return (EmObject *)ht;
}

EmObject *
newhashobject() {
    return newhashobject_from_size(DEFAULT_HASH_SIZE);
}

void
hashobject_free(EmObject * ob)
{
    if (!is_EmHashObject(ob)) {
        log_error(TYPE_ERROR, "hash free on non-hash object");
        return;
    }
    int i;
    EmHashObject *ho = (EmHashObject *)ob;
    for(i=0;i<ho->size;i++) {
        if( ho->table[i]) {
            // free entry elements by decrease their reference count
            DECREF(ho->table[i]->key);
            DECREF(ho->table[i]->val);
            DEL(ho->table[i]); // free the entry root
        }
    }
    DEL( ho->table );
    DEL( ho );
}

void hashobject_print(EmObject * ob, FILE *fp) {
    if (!is_EmHashObject(ob)) {
        log_error(TYPE_ERROR, "hash print on non-hash object");
        return;
    }
    EmHashObject *ho = (EmHashObject *)ob;

    int i;
    for (i = 0; i < ho->size; i++) {
        if (ho->table[i] != NULL) {
            fprintf(fp, "%s:    %s\n", tostrobj(ho->table[i]->key),
                    tostrobj(ho->table[i]->val));
        }
    }
}

/*
 * This is the internal lookup function used by other wrapper function.
 */
static EmHashEntry *
__hashobject_lookup(EmHashObject *ho, EmObject *key, unsigned int *idx)
{
    unsigned long hashval;
    unsigned int incr;

    // calculate the hash
    hashval = hashobj(key);
    *idx = hashval % ho->size;

    // calculate the increment for linear probing
    do {
        hashval = hashval + hashval + 1;
        incr = hashval % ho->size;
    } while (incr ==0 );

    // If the spot is occupied and not equal to this key
    while( ho->table[*idx] != NULL
            && cmpobj(key, ho->table[*idx]->key) != 0 ) {
        *idx = (*idx+incr) % ho->size;
    }

    // Do we have this key or not
    if( ho->table[*idx] == NULL ) {
        return NULL;
    } else {
        return ho->table[*idx];
    }
}

/*
 * The lookup uses an object as a key. The object types can be string, integer or
 * any other types that can be used as key.
 */
EmObject *
hashobject_lookup(EmObject *ob, EmObject *key) {
    if (!is_EmHashObject(ob)) {
        log_error(TYPE_ERROR, "hash lookup on non-hash object");
        return NULL;
    }
    unsigned int idx;
    EmHashObject *ho = (EmHashObject *)ob;
    EmHashEntry * ent = __hashobject_lookup(ho, key, &idx);
    if (ent == NULL)
        return log_error(KEY_ERROR, "key not found");
    else {
        INCREF(ent->val);
        return ent->val;
    }
}

int
hashobject_haskey(EmObject *ob, EmObject *key) {
    unsigned int idx;
    EmHashObject *ho = (EmHashObject *) ob;
    EmHashEntry * ent = __hashobject_lookup(ho, key, &idx);
    if (ent == NULL)
        return 0;
    else
        return 1;
}

static EmHashObject *
hashobject_rehash(EmHashObject *ho)
{
    EmHashObject * newho;
    unsigned int size;
    int i;

    /* calculate new hash table size based on load factor */
    size = ho->nitems * 2u;  // 50% load
    newho = (EmHashObject *)newhashobject_from_size(size);

    /* rehash the values on the old hash table */
    for (i = 0; i < ho->size; i++) {
        if (ho->table[i] != NULL) {
            hashobject_insert((EmObject *)newho,
                    ho->table[i]->key, ho->table[i]->val);
        }
    }
    hashobject_free((EmObject *)ho);
    return newho;
}

EmObject *
hashobject_insert(EmObject *ob, EmObject *key, EmObject *val) {

    if (!is_EmHashObject(ob)) {
        log_error(TYPE_ERROR, "hash free on non-hash object");
        return NULL;
    }
    EmHashObject *ho = (EmHashObject *)ob;

    unsigned long hashval;
    unsigned int idx;
    EmHashEntry* new;

    /* rehash if too full */
    if( ho->nitems*3 > ho->size*2) {
        ho = hashobject_rehash(ho);
    }

    new = __hashobject_lookup(ho, key, &idx);

    if (new == NULL) { // create new entry
        new = (EmHashEntry*) malloc(sizeof(EmHashEntry));
        if (new == NULL) {
            log_error(MEMORY_ERROR, "No memory to create new entry in dict");
            return (EmObject *)ho;
        }
        new->key = key;
        new->val = val;
        // always retain references to the new key and val
        INCREF(key);
        INCREF(val);
        ho->table[idx] = new;
        ho->nitems++;
    } else { // replace old entry
        DECREF(ho->table[idx]->val);
        ho->table[idx]->val = val;
        INCREF(val);
    }

    return (EmObject *)ho;
}

int
hashobject_delete(EmObject *ob, EmObject *key) {
    if (!is_EmHashObject(ob)) {
        log_error(TYPE_ERROR, "hash free on non-hash object");
        return 0;
    }
    unsigned int idx;
    EmHashObject *ho = (EmHashObject *)ob;
    EmHashEntry *found = __hashobject_lookup(ho, key, &idx);
    if (found) {
        DECREF(found->key);
        DECREF(found->val);
        DEL(found);
        return 1;
    } else {
        log_error(KEY_ERROR, "key not found");
        return 0;
    }
}

/*
 * Convenience function for String keys
 */
EmObject *
hashobject_lookup_by_string(EmObject *ho, char *key) {
    EmObject *obkey = newstringobject(key);
    EmObject *ob = hashobject_lookup(ho, obkey);
    DECREF(obkey); // release the key after use
    return ob;
}

int
hashobject_haskey_by_string(EmObject *ho, char *key) {
    EmObject *obkey = newstringobject(key);
    int res = hashobject_haskey(ho, obkey);
    DECREF(obkey); // release the key after use
    return res;
}

EmObject *
hashobject_insert_by_string(EmObject *ho, char *key, EmObject *val) {
    EmObject *obkey = newstringobject(key);
    ho = hashobject_insert(ho, obkey, val);
    DECREF(obkey);
    return ho;
}

int
hashobject_delete_by_string(EmObject *ho, char *key) {
    EmObject *obkey = newstringobject(key);
    int ret = hashobject_delete(ho, obkey);
    DECREF(obkey); // release the key after use
    return ret;
}


/*
 * Mapping functions
 */
unsigned int
hashobject_mp_len(EmObject *ob) {
    return ((EmHashObject *)ob)->nitems;
}

static EmMappingMethods hash_as_mapping = {
        hashobject_mp_len, // map length
        0,
        0,
};

EmTypeObject Hashtype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // nitems
        "hash",                         // tp_name
        sizeof(EmHashObject),           // tp_size
        0,                              // tp_itemsize

        hashobject_free,                // tp_dealloc
        hashobject_print,               // tp_print
        0,                              // tp_tostr
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        0,                              // tp_hashfunc

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        &hash_as_mapping,               // tp_as_mapping
};

