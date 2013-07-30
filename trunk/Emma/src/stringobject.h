/*
 * stringobject.h
 *
 *  Created on: 29/07/2013
 *      Author: ywangd
 */

#ifndef STRINGOBJECT_H_
#define STRINGOBJECT_H_

extern EmTypeObject Stringtype;
typedef struct _stringobject EmStringObject;

EmStringObject *newstringobject(char *sval);
EmStringObject *newstringobject_from_int(long ival);
EmStringObject *newstringobject_from_float(double fval);

#endif /* STRINGOBJECT_H_ */
