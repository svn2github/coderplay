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

EmObject *newstringobject(char *sval);
EmObject *newstringobject_from_int(long ival);
EmObject *newstringobject_from_float(double fval);
char *getstringvalue(EmObject *ob);

#endif /* STRINGOBJECT_H_ */
