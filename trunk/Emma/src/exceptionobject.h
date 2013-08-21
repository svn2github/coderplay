/*
 * exceptionobject.h
 *
 *  Created on: 21/08/2013
 *      Author: ywangd
 */

#ifndef EXCEPTIONOBJECT_H_
#define EXCEPTIONOBJECT_H_

#define ex_nomem(msg,val)       set_exception(MemoryException, msg, val)
#define ex_badtype(msg,val)     set_exception(TypeException, msg, val)

typedef struct _exceptionobject {
    OB_HEAD;
    EmObject *errtype;
    EmObject *message;
    EmObject *value;
} EmExceptionObject;

extern EmTypeObject Exceptiontype;

extern EmObject *MemoryException;
extern EmObject *SystemException;
extern EmObject *TypeException;
extern EmObject *KeyException;
extern EmObject *IndexException;
extern EmObject *RuntimeException;

extern EmObject *last_exception;

EmObject *newexceptionobject(char *errtype, char *message);
void set_exception(EmObject *ob, char *message, char *value);
void print_exception();
void clear_exception();


#endif /* EXCEPTIONOBJECT_H_ */
