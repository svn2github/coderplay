/*
 * =====================================================================================
 *
 *       Filename:  datatype.h
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  10/27/2011 10:55:56 PM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  ywangd (sonickenking), ywangd@gmail.com
 *        Company:  
 *
 * =====================================================================================
 */

#define FREE_DATA_PTR_WHEN_DELETE       1
#define KEEP_DATA_PTR_WHEN_DELETE       0

/* Define the data type that the code can be evaluated to */
typedef enum
{
    DT_NUM = 258,
    DT_STR,
    DT_SYM,
    DT_NUL
} datatypeEnum;

typedef struct {
    datatypeEnum dataType;
    void *data;
    int gcdata;
} dataobj_t;

dataobj_t *create_dataobj(datatypeEnum type, void *data, int gcdata);
void delete_dataobj(dataobj_t *dobj);
void print_dataobj (dataobj_t * dobj);
dataobj_t * get_data_from_symbol(symbol_t *sym); 


