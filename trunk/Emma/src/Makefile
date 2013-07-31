
CC=gcc
CFLAGS=-g
DEPS = lexer.h token.h lexer.i hashobject.h errorobject.h stringobject.h \
       object.h allobject.h
SRC = lexer.c parser.c Emma.c hashobject.c errobject.c stringobject.c \
      object.c typeobject.c
OBJ = lexer.o parser.o Emma.o hashobject.o errorobject.o stringobject.o \
      object.o typeobject.o

all: Emma

Emma: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

.PHONY: clean

clean:
	rm -f *.o Emma
