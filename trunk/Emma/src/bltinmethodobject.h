/*
 * bltinmethodobject.h
 *
 *  Created on: 19/08/2013
 *      Author: ywang@gmail.com
 */

#ifndef BLTINMETHODOBJECT_H_
#define BLTINMETHODOBJECT_H_


typedef EmObject * (*bo_method)(EmObject *, EmObject *);



typedef struct _bltinmethodobject {
    OB_HEAD;
    EmObject *name;
    bo_method method;
    EmObject *self;
} EmBltinmethodObject;


extern EmTypeObject Bltinmethodtype;

EmObject *newbltinmethodobject();

typedef struct _methodlist {
    char *name;
    bo_method meth;
} Methodlist;

#endif /* BLTINMETHODOBJECT_H_ */
