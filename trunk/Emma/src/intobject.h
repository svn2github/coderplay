/*
 * intobject.h
 *
 *  Created on: 31/07/2013
 *      Author: ywangd
 */

#ifndef INTOBJECT_H_
#define INTOBJECT_H_

extern EmTypeObject Inttype;
typedef struct _intobject EmIntObject;

EmIntObject *newintobject(long ival);


#endif /* INTOBJECT_H_ */
