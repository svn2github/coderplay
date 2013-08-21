
CC=gcc
CFLAGS=-g
LIBS=-lm
DEPS = Makefile lexer.h token.h lexer.i hashobject.h errorobject.h \
       stringobject.h object.h Emma.h intobject.h floatobject.h \
       listobject.h source.h token.h parser.h parser.hi parser.i \
       node.h ast.h ast.hi ast.i opcode.h opcode.hi opcode.i compiler.h \
       codeobject.h fileobject.h moduleobject.h bltinmethodobject.h \
       exceptionobject.h bltinmodule.h vm.h
       
SRC = lexer.c parser.c Emma.c hashobject.c errobject.c stringobject.c \
      object.c typeobject.c intobject.c floatobject.c listobject.c \
      source.c parser.c node.c ast.c compiler.c codeobject.c fileobject.c \
      moduleobject.c bltinmethodobject.c exceptionobject.c \
      bltinmodule.c vm.c
      
OBJ = lexer.o parser.o Emma.o hashobject.o errorobject.o stringobject.o \
      object.o typeobject.o intobject.o floatobject.o listobject.o \
      source.o parser.o node.o ast.o compiler.o codeobject.o fileobject.o \
      moduleobject.o bltinmethodobject.o exceptionobject.o \
      bltinmodule.c vm.o

all: Emma

Emma: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LIBS)

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

allobject.h: $(DEPS)

.PHONY: clean

clean:
	rm -f *.o Emma
