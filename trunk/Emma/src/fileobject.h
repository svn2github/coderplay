/*
 * fileobject.h
 *
 *  Created on: 17/08/2013
 *      Author: ywangd
 */

#ifndef FILEOBJECT_H_
#define FILEOBJECT_H_


typedef struct _fileobject {
    OB_HEAD;
    FILE *fp;
    EmObject *name;
} EmFileObject;

extern EmTypeObject Filetype;

EmObject *newfileobject(FILE *fp, char *name);




#endif /* FILEOBJECT_H_ */
