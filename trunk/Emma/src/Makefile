
CC=gcc
CFLAGS=
DEPS = lexer.h token.h wordstable.h lexer.i token.i
SRC = wordstable.c lexer.c parser.c token.c
OBJ = wordstable.o lexer.o parser.o token.o

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

emma: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)


.PHONY: clean

clean:
	rm -f *.o emma
