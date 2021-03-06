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

EmObject *newfloatobject(double val);
double getfloatvalue(EmObject *ob);


#endif /* FLOATOBJECT_H_ */
