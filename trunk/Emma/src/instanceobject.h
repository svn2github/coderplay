/*
 * instanceobject.h
 *
 *  Created on: 26/08/2013
 *      Author: ywangd
 */

#ifndef INSTANCEOBJECT_H_
#define INSTANCEOBJECT_H_

typedef struct _instanceobject {
    OB_HEAD;
    EmObject *class; // the class of the instance
    EmObject *attr; // hash
} EmInstanceObject;

extern EmTypeObject Instancetype;

EmObject *newinstanceobject(EmObject *class);



typedef struct _instancemethodobject {
    OB_HEAD;
    EmObject *self;
    EmObject *func;
} EmInstancemethodObject;

extern EmTypeObject Instancemethodtype;

EmObject *newinstancemethodobject(EmObject *self, EmObject *func);


#endif /* INSTANCEOBJECT_H_ */
