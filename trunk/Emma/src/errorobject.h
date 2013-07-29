/*
 * errorobject.h
 *
 *  Created on: 29/07/2013
 *      Author: ywang@gmail.com
 */

#ifndef ERROROBJECT_H_
#define ERROROBJECT_H_

#define NO_ERROR        0
#define MEMORY_ERROR    1
#define SYSTEM_ERROR    2
#define TYPE_ERROR      3
#define KEY_ERROR       4

// The singleton error object
extern struct _errorobject errobj;

int log_error(int errorNumber, char *message);

#endif /* ERROROBJECT_H_ */
