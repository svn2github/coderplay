/*
 * classobject.h
 *
 *  Created on: 25/08/2013
 *      Author: ywangd
 */

#ifndef CLASSOBJECT_H_
#define CLASSOBJECT_H_


typedef struct _classobject {
    OB_HEAD;
    EmObject *base;
    EmObject *attr;
} EmClassObject;

extern EmTypeObject Classtype;

EmObject *newclassobject();



#endif /* CLASSOBJECT_H_ */
