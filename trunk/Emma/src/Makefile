
CC=gcc
CFLAGS=-g
DEPS = lexer.h token.h lexer.i hashobject.h errorobject.h stringobject.h \
       object.h Emma.h intobject.h floatobject.h
       
SRC = lexer.c parser.c Emma.c hashobject.c errobject.c stringobject.c \
      object.c typeobject.c intobject.c floatobject.c
      
OBJ = lexer.o parser.o Emma.o hashobject.o errorobject.o stringobject.o \
      object.o typeobject.o intobject.o floatobject.o

all: Emma

Emma: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

allobject.h: $(DEPS)

.PHONY: clean

clean:
	rm -f *.o Emma
