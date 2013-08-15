/*
 * vm.c
 *
 *  Created on: 16/08/2013
 *      Author: ywangd
 */


#define NEXT_INSTR(co,pc)       (co)->code[pc++]
#define NEXT_ARG(co,pc)         (pc+=2, ((co)->code[pc-1] << 8) + (co)->code[pc-2])


int run(EmCodeObject *co) {



    return 1;
}
