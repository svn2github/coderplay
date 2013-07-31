/*
 * stringobject.h
 *
 *  Created on: 29/07/2013
 *      Author: ywangd
 */

#ifndef STRINGOBJECT_H_
#define STRINGOBJECT_H_

typedef struct _stringobject {
    OB_HEAD; // nitems included
    char *sval;
} EmStringObject;

extern EmTypeObject Stringtype;

EmStringObject *newstringobject(char *sval);
EmStringObject *newstringobject_from_int(long ival);
EmStringObject *newstringobject_from_float(double fval);

#endif /* STRINGOBJECT_H_ */
