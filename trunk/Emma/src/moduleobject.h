/*
 * moduleobject.h
 *
 *  Created on: 19/08/2013
 *      Author: ywang@gmail.com
 */

#ifndef MODULEOBJECT_H_
#define MODULEOBJECT_H_


typedef struct _moduleobject {
    OB_HEAD;
    EmObject *name;
    EmObject *hash;
} EmModuleObject;

extern EmTypeObject Moduletype;

EmObject *newmoduleobject();



#endif /* MODULEOBJECT_H_ */
