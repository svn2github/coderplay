/*
 * bltinmodule.h
 *
 *  Created on: 19/08/2013
 *      Author: ywang@gmail.com
 */

#ifndef BLTINMODULE_H_
#define BLTINMODULE_H_

typedef struct _bltinmethod_params_desc {
    int nargs;
    int nreq_args;
    char keywords[200]; // keywords separated by whitespace
}BltinmethodParamsDesc;

#endif /* BLTINMODULE_H_ */
