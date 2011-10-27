CC = gcc
LEX = flex
YACC = bison

# Delete the default suffixes
.SUFFIXES:  

.PHONY: all clean

all: epw

epw: epw.h epw.c lexer.o
	$(CC) -c epw.c
	$(CC) -o epw parser.o lexer.o epw.o -lfl

lexer.o: epw.l epw.y
	$(YACC) -d --report=all -g --output=parser.c epw.y
	$(LEX) -olexer.c epw.l
	$(CC) -c parser.c lexer.c

clean:
	rm -f epw *.o parser.* lexer.c
