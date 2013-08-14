/*
 * funcobject.h
 *
 *  Created on: 15/08/2013
 *      Author: ywangd
 */

#ifndef FUNCOBJECT_H_
#define FUNCOBJECT_H_

typedef struct _funcobject {
    OB_HEAD;
    EmObject *code;
} EmFuncObject;

extern EmFuncObject Functype;

EmObject *newfuncobject();



#endif /* FUNCOBJECT_H_ */
