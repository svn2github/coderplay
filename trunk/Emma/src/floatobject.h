/*
 * floatobject.h
 *
 *  Created on: 31/07/2013
 *      Author: ywangd
 */

#ifndef FLOATOBJECT_H_
#define FLOATOBJECT_H_


extern EmTypeObject Floattype;
typedef struct _intobject EmFloatObject;

EmFloatObject *newfloatobject(double val);


#endif /* FLOATOBJECT_H_ */
