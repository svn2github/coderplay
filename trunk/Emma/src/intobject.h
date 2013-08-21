/*
 * intobject.h
 *
 *  Created on: 31/07/2013
 *      Author: ywangd
 */

#ifndef INTOBJECT_H_
#define INTOBJECT_H_


typedef struct _intobject {
    OB_HEAD;
    long ival;
} EmIntObject;

extern EmTypeObject Inttype;

EmObject *newintobject(long ival);
long getintvalue(EmObject *ob);


#endif /* INTOBJECT_H_ */
