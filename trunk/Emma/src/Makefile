
CC=gcc
CFLAGS=-g
DEPS = lexer.h token.h lexer.i
SRC = lexer.c parser.c Emma.c
OBJ = lexer.o parser.o Emma.o

all: Emma

Emma: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

.PHONY: clean

clean:
	rm -f *.o Emma
