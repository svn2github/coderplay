#include "allobject.h"

typedef struct {
    EmObject *key;
    EmObject *val;
} EmHashEntry;

typedef struct _hashobject {
    OB_HEAD; // nitems included
    unsigned int size; // size of the hash including unused spots
    EmHashEntry **table; // the entry array
} EmHashObject;

static unsigned int prime_numbers[] = {
    3, 7, 13, 31, 61, 127, 251, 509, 1021, 2017, 4093,
    5987, 9551, 15683, 19609, 31397, 59999,
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

EmHashObject *
hashobject_new(unsigned int size) {

    if (!(size = ht_getprime(size))) {
        memory_error("hash table size overflow");
        return NULL;
    }
    EmHashObject *ht = OBJECT_NEW(EmHashObject, &Hashtype);
    ht->size = size;
    ht->nitems = 0;

    ht->table = (EmHashEntry **) calloc (ht->size, sizeof(EmHashEntry *));
    if (ht->table == NULL) {
        OBJECT_FREE(ht);
        return log_error(MEMORY_ERROR, "not enough memory for hashtable");
    }

    return ht;
}

void
hashobject_free(EmHashObject * ht)
{
    int i;
    for(i=0;i<ht->size;i++) {
        if( ht->table[i] != NULL) {
            // free entry elements
            DECREF(ht->table[i]->key);
            DECREF(ht->table[i]->val);
            free(ht->table[i]); // free the entry root
        }
    }
    free( ht->table );
    free( ht );
}

EmObject *
hashobject_lookup(EmHashObject *ht, EmObject *key)
{
    unsigned long hashval;
    unsigned int idx, incr;

    /* calculate the hash function */
    if (key->type->tp_hashfunc)
        hashval = key->type->tp_hashfunc(key);
    else {
        return log_error(TYPE_ERROR, "unhashable type");
    }
    idx = hashval % ht->size;
    // calculate the increment for linear probing
    do {
        hashval = hashval + hashval + 1;
        incr = hashval % ht->size;
    } while (incr ==0 );

    // If the spot is occupied and not equal to this key
    while( ht->table[idx] != NULL
            && key->type->tp_compare(key, ht->table[idx]->key) != 0 ) {
        idx = (idx+incr) % ht->size;
    }

    // Do we have this key or not
    if( ht->table[idx] == NULL ) {
        return log_error(KEY_ERROR, "key not found");
    } else {
        return ht->table[idx]->val;
    }
}

EmHashObject *
hashobject_insert(EmHashObject * ht, EmObject *key, EmObject *val) {

    unsigned long hashval;
    unsigned int idx, incr;
    EmHashEntry* new;

    /* rehash if too full */
    if( ht->nitems*3 > ht->size*2) {
        ht = hashobject_rehash(ht);
    }

    /* calculate the hash function */
    if (key->type->tp_hashfunc)
        hashval = key->type->tp_hashfunc(key);
    else {
        log_error(TYPE_ERROR, "unhashable type");
        return ht;
    }

    idx = hashval % ht->size;
    // calculate the increment for linear probing
    do {
        hashval = hashval + hashval + 1;
        incr = hashval % ht->size;
    } while (incr ==0 );

    /* insert with linear probing */
    while( ht->table[idx] != NULL
            && key->type->tp_compare(key, ht->table[idx]->key) != 0 ) {
        idx = (idx+incr) % ht->size;
    }

    // insert if new or replace if exists
    if( ht->table[idx] == NULL ) { // insert new key
        new = (EmHashEntry*) malloc(sizeof(EmHashEntry));
        if (!new) {
            log_error(MEMORY_ERROR, "No memory to create new entry");
            return ht;
        }
        new->key = key; INCREF(key);
        new->val = val; INCREF(val);
        ht->table[idx] = new;
        ht->nitems++;
    } else { // replace old key
        DECREF(ht->table[idx]->key);
        DECREF(ht->table[idx]->val);
        ht->table[idx]->key = key;
        ht->table[idx]->val = val;
    }

    return ht;
}

EmTypeObject Hashtype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
        0,                              // base
        0,                              // nitems
        "hash",                         // tp_name
        sizeof(EmHashObject),           // tp_size
        0,                              // tp_itemsize

        0,                              // tp_alloc
        0,                              // tp_dealloc
        0,                              // tp_print
        0,                              // tp_str
        0,                              // tp_getattr
        0,                              // tp_setattr
        0,                              // tp_compare
        0,                              // tp_hashfunc

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        0,                              // tp_as_mapping
};

