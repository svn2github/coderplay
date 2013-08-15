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
    EmObject *co;
    EmObject *extrap; // the variable name for extrap
    EmObject *extrak; // the variable name for extrak
    EmObject *globals;
    EmObject *locals;

} EmFuncObject;

extern EmFuncObject Functype;

EmObject *newfuncobject();



#endif /* FUNCOBJECT_H_ */
