
CC=gcc
CFLAGS=-g
DEPS = lexer.h token.h wordstable.h lexer.i token.i
SRC = wordstable.c lexer.c parser.c token.c Emma.c
OBJ = wordstable.o lexer.o parser.o token.o Emma.o

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

Emma: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)


.PHONY: clean

clean:
	rm -f *.o Emma
