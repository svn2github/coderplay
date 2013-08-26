/*
 * funcobject.h
 *
 *  Created on: 15/08/2013
 *      Author: ywangd
 */

#ifndef FUNCOBJECT_H_
#define FUNCOBJECT_H_

#define is_EmFuncObject(ob)      ((ob)->type == &Functype)

struct _environment;
extern void env_free(struct _environment *);

typedef struct _funcobject {
    OB_HEAD;
    EmObject *co;
    struct _environment *env; // the environment where the function is defined

} EmFuncObject;

extern EmTypeObject Functype;

EmObject *newfuncobject(EmObject *co, struct _environment *env);


#endif /* FUNCOBJECT_H_ */
