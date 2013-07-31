/*
 * floatobject.h
 *
 *  Created on: 31/07/2013
 *      Author: ywangd
 */

#ifndef FLOATOBJECT_H_
#define FLOATOBJECT_H_


typedef struct _floatobject {
    OB_HEAD;
    double fval;
} EmFloatObject;

extern EmTypeObject Floattype;

EmFloatObject *newfloatobject(double val);


#endif /* FLOATOBJECT_H_ */
