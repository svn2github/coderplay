#include "allobject.h"

/*
 * TODO:
 * 1. May save hash value of the key, so comparison and especially rehash
 *    can be faster.
 * 2. Use dummy entry so I don't have to dealloc when deleting keys.
 * 3. Some records of the keys, so I don't have to loop all slots to find
 *    filled entries.
 */
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

EmHashObject *
hashobject_new(unsigned int size) {

    if (!(size = ht_getprime(size))) {
        log_error(MEMORY_ERROR, "hash table size overflow");
        return NULL;
    }

    EmHashObject *ht = NEWOBJ(EmHashObject, &Hashtype);
    if (ht == NULL)
        return NULL;

    ht->size = size;
    ht->nitems = 0;

    ht->table = (EmHashEntry **) calloc (ht->size, sizeof(EmHashEntry *));
    if (ht->table == NULL) {
        free(ht);
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
            // free entry elements by decrease their reference count
            DECREF(ht->table[i]->key);
            DECREF(ht->table[i]->val);
            free(ht->table[i]); // free the entry root
        }
    }
    free( ht->table );
    free( ht );
}

/*
 * This is the internal lookup function used by other wrappers
 */
static EmObject *
__hashobject_lookup(EmHashObject *ht, EmObject *key)
{
    unsigned long hashval;
    unsigned int idx, incr;

    // calculate the hash
    hashval = hashobj(key);
    idx = hashval % ht->size;

    // calculate the increment for linear probing
    do {
        hashval = hashval + hashval + 1;
        incr = hashval % ht->size;
    } while (incr ==0 );

    // If the spot is occupied and not equal to this key
    while( ht->table[idx] != NULL
            && cmpobj(key, ht->table[idx]->key) != 0 ) {
        idx = (idx+incr) % ht->size;
    }

    // Do we have this key or not
    if( ht->table[idx] == NULL ) {
        return NULL;
    } else {
        return ht->table[idx]->val;
    }
}

EmObject *
hashobject_lookup(EmHashObject *ht, EmObject *key) {
    EmHashEntry * ent = __hashobject_lookup(EmHashObject *ht, EmObject *key);
    if (ent == NULL)
        return log_error(KEY_ERROR, "key not found");
    else
        return ent->val;
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

    new = __hashobject_lookup(EmHashObject *ht, EmObject *key);

    if (new == NULL) { // create new entry
        new = (EmHashEntry*) malloc(sizeof(EmHashEntry));
        if (new == NULL) {
            log_error(MEMORY_ERROR, "No memory to create new entry in dict");
            return ht;
        }
        new->key = key;
        new->val = val;
        INCREF(key);
        INCREF(val);
        ht->table[idx] = new;
        ht->nitems++;
    } else { // replace old entry
        DECREF(ht->table[idx]->key);
        DECREF(ht->table[idx]->val);
        ht->table[idx]->key = key;
        ht->table[idx]->val = val;
    }

    return ht;
}

EmHashObject *
hashobject_rehash(EmHashObject * ht)
{
    EmHashObject * newht;
    int size,i;

    /* calculate new hash table size based on load factor */
    size = ht_getprime(ht->nitems * 2);  // 50% load
    newht = hashobject_new(size);

    /* rehash the values on the old hash table */
    for (i = 0; i < ht->size; i++) {
        if (ht->table[i] != NULL) {
            hashobject_insert(newht, ht->table[i]->key, ht->table[i]->val);
        }
    }
    hashobject_free(ht);
    return newht;
}

void hashobject_print(EmHashObject * ht, FILE *fp) {
    int i;
    for (i = 0; i < ht->size; i++) {
        if (ht->table[i] != NULL) {
            fprintf(fp, "%20s :   %20d\n", tostrobj(ht->table[i]->key),
                    tostrobj(ht->table[i]->val));
        }
    }
}


/*
 * Wrapper function for String ONLY keys
 */
EmObject *
hashobject_lookup_by_string(EmHashObject *ht, char *key) {
    EmStringObject *obkey = stringobject_new(key);
    return hashobject_lookup(ht, obkey);
}

EmTypeObject Hashtype = {
        OB_HEAD_INIT(&Typetype),        // set type and refcnt to 1
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

