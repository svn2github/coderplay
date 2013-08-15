/*
 * codeobject.h
 *
 *  Created on: 15/08/2013
 *      Author: ywangd
 */

#ifndef CODEOBJECT_H_
#define CODEOBJECT_H_


typedef struct _codeobject {
    OB_HEAD;
    char *code;
    int nbytes;
    EmObject *consts;
    EmObject *names;
} EmCodeObject;

extern EmTypeObject Codetype;

EmObject *newcodeobject(int nbytes);


#endif /* CODEOBJECT_H_ */
