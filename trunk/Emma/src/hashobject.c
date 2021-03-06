#include "allobject.h"

/*
 * TODO:
 * 1. May save hash value of the key, so comparison and especially rehash
 *    can be faster.
 * 2. Use dummy entry so I don't have to dealloc when deleting keys.
 * 3. Some records of the keys, so I don't have to loop all slots to find
 *    filled entries.
 */

static int prime_numbers[] = {
    7, 13, 31, 61, 127, 251, 509, 1021, 2017, 4093,
    5987, 9551, 15683, 19609, 31397, // 59999,
};

static int npnumbers = sizeof(prime_numbers) / sizeof(int);

int ht_getprime(int size) {
    int ii;
    for (ii=0; ii< npnumbers; ii++) {
        if (prime_numbers[ii] >= size)
            return prime_numbers[ii];
    }
    return 0;
}

EmObject *
newhashobject_from_size(int size_req) {
    EmHashObject *ht;
    int size;

    if (!(size = ht_getprime(size_req))) {
        ex_mem("hash table size overflow");
        return NULL;
    }

    if ((ht = NEWOBJ(EmHashObject, &Hashtype)) == NULL) {
        printf("no memory for new hash\n");
        return NULL;
    }

    ht->size = size;
    ht->nitems = 0;

    if ((ht->table = (EmHashEntry **) calloc(ht->size, sizeof(EmHashEntry *)))
            == NULL) {
        DEL(ht);
        ex_mem("not enough memory for hashtable");
        return NULL;
    }
    return (EmObject *)ht;
}

EmObject *
newhashobject_from_list(EmObject *ob) {
    int size = listobject_len(ob);
    if (size % 2 != 0) {
        ex_runtime("number of list items must be even");
        return NULL;
    }
    EmObject *ho = newhashobject_from_size(0);

    EmObject *k, *v;
    int ii;
    for (ii = 0; ii < size; ii += 2) {
        k = listobject_get(ob, ii);
        v = listobject_get(ob, ii+1);
        hashobject_insert(ho, k, v);
        DECREF(k);
        DECREF(v);
    }
    return ho;
}


EmObject *
newhashobject() {
    return newhashobject_from_size(DEFAULT_HASH_SIZE);
}

void
hashobject_free(EmObject * ob)
{
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

    EmHashObject *ho = (EmHashObject *)ob;

    int i, count = 0;
    fprintf(fp, "{");
    for (i = 0; i < ho->size; i++) {
        if (ho->table[i] != NULL) {
            printobj(ho->table[i]->key, fp);
            fprintf(fp, ":    ");
            printobj(ho->table[i]->val, fp);
            if (count < ho->nitems-1)
                fprintf(fp, ", ");
            count++;
        }
    }
    fprintf(fp, "}");
}

/*
 * This is the internal lookup function used by other wrapper function.
 */
static EmHashEntry *
__hashobject_lookup(EmHashObject *ho, EmObject *key, int *idx)
{
    unsigned long hashval;
    int incr;

    // calculate the hash
    hashval = hashobj(key);
    if (hashval < 0) {
        return NULL;
    }
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
        ex_type("wrong type for hash lookup");
        return NULL;
    }

    int idx;
    EmHashObject *ho = (EmHashObject *)ob;
    EmHashEntry * ent = __hashobject_lookup(ho, key, &idx);
    if (ent == NULL)
        return NULL;
    else {
        INCREF(ent->val);
        return ent->val;
    }
}

int
hashobject_haskey(EmObject *ob, EmObject *key) {
    int idx;
    EmHashObject *ho = (EmHashObject *) ob;
    EmHashEntry * ent = __hashobject_lookup(ho, key, &idx);
    if (ent == NULL)
        return 0;
    else
        return 1;
}

static int
hashobject_rehash(EmHashObject *ho)
{
    int newsize, oldsize;
    EmHashEntry **newtable, **oldtable;

    /* calculate new hash table size based on load factor */
    newsize = ht_getprime(ho->nitems * 2u);  // 50% load

    newtable = (EmHashEntry **) calloc(newsize, sizeof(EmHashEntry *));
    if (newtable == NULL) {
        return 0;
    }

    oldtable = ho->table;
    oldsize = ho->size;

    ho->table = newtable;
    ho->size = newsize;
    ho->nitems = 0;


    /* rehash the values on the old hash table */
    int i;
    for (i = 0; i < oldsize; i++) {
        if (oldtable[i] != NULL) {
            hashobject_insert((EmObject *)ho,
                    oldtable[i]->key, oldtable[i]->val);
            DECREF(oldtable[i]->key);
            DECREF(oldtable[i]->val);
            DEL(oldtable[i]); // free the entry root
        }
    }
    DEL(oldtable);
    return 1;
}

int
hashobject_insert(EmObject *ob, EmObject *key, EmObject *val) {

    if (!is_EmHashObject(ob)) {
        ex_type("wrong type for hash insert");
        return 0;
    }
    EmHashObject *ho = (EmHashObject *)ob;

    unsigned long hashval;
    int idx;
    EmHashEntry* new;

    /* rehash if too full */
    if( ho->nitems*3 > ho->size*2) {
        if (hashobject_rehash(ho) == 0) {
            return 0;
        }
    }

    new = __hashobject_lookup(ho, key, &idx);

    if (new == NULL) { // create new entry
        new = (EmHashEntry*) malloc(sizeof(EmHashEntry));
        if (new == NULL) {
            ex_mem("No memory to create new entry of hash");
            return 0;
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

    return 1;
}

int
hashobject_delete(EmObject *ob, EmObject *key) {
    if (!is_EmHashObject(ob)) {
        ex_type("wrong type for hash entry delete");
        return 0;
    }
    int idx;
    EmHashObject *ho = (EmHashObject *)ob;
    EmHashEntry *found = __hashobject_lookup(ho, key, &idx);
    if (found) {
        DECREF(found->key);
        DECREF(found->val);
        DEL(found);
        ho->table[idx] = NULL;
        ho->nitems--;
        return 1;
    } else {
        ex_key("key not found");
        return 0;
    }
}

int
hashobject_len(EmObject *ob) {
    return ob->nitems;
}

EmObject *
hashobject_keys(EmObject *ob) {
    EmHashObject *ho = (EmHashObject *)ob;

    EmObject *lo = newlistobject(ho->nitems);
    int i;
    for (i = 0; i < ho->size; i++) {
        if (ho->table[i] != NULL) {
            listobject_append(lo, ho->table[i]->key);
        }
    }
    return lo;
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

int
hashobject_insert_by_string(EmObject *ho, char *key, EmObject *val) {
    EmObject *obkey = newstringobject(key);
    int retval;
    retval = hashobject_insert(ho, obkey, val);
    DECREF(obkey);
    return retval;
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
int
hashobject_mp_len(EmObject *ob) {
    return ((EmHashObject *)ob)->nitems;
}

static EmMappingMethods hash_as_mapping = {
        hashobject_mp_len, // map length
        0,
        0,
};

int hashobject_boolean(EmObject *ob) {
    return ((EmHashObject *)ob)->nitems > 0 ? 1 : 0;
}

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
        0,                              // tp_boolean

        0,                              // tp_as_number
        0,                              // tp_as_sequence
        &hash_as_mapping,               // tp_as_mapping
};

