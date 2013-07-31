
CC=gcc
CFLAGS=-g
DEPS = lexer.h token.h wordstable.h lexer.i token.i
SRC = wordstable.c lexer.c parser.c token.c Emma.c
OBJ = wordstable.o lexer.o parser.o token.o Emma.o

all: Emma

Emma: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

.PHONY: clean

clean:
	rm -f *.o Emma
