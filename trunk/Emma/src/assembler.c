/*
 * assembler.c
 *
 *  Created on: 13/08/2013
 *      Author: ywangd
 */

#include "Emma.h"

//static int
//c_resize_code(CompiledUnit *c) {
//    c->code =
//            (unsigned char *) realloc(c->code,
//                    (c->len + 1000) * sizeof(unsigned char));
//    if (c->code == NULL) {
//        log_error(MEMORY_ERROR, "no memory to increase code length");
//        return 0;
//    }
//    c->len += 1000;
//    return 1;
//}

//static void
//c_addbyte(CompiledUnit *c, int byte) {
//    if (byte < 0 || byte > 255) {
//        fatal("trying to add invalid byte to code");
//    }
//    if (c->nexti >= c->len) {
//        c_resize_code(c);
//    }
//    c->code[c->nexti++] = byte;
//}
//
//static void
//c_addint(CompiledUnit *c, int i) {
//    if (i < 0) {
//        fatal("trying to add invalid int to code");
//    }
//    c_addbyte(c, i & 0xff);
//    c_addbyte(c, i >> 8);
//}
