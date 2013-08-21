/*
 * exceptionobject.h
 *
 *  Created on: 21/08/2013
 *      Author: ywangd
 */

#ifndef EXCEPTIONOBJECT_H_
#define EXCEPTIONOBJECT_H_


typedef struct _exceptionobject {
    OB_HEAD;
    EmObject *errtype;
    EmObject *message;
    EmObject *value;
} EmExceptionObject;

extern EmTypeObject Exceptiontype;

extern EmObject *last_exception;

EmObject *newexceptionobject(char *errtype, char *message);
void exceptionobject_free(EmObject *ob);


#endif /* EXCEPTIONOBJECT_H_ */
