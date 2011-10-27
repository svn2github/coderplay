CC = gcc
LEX = flex
YACC = bison

# Delete the default suffixes
.SUFFIXES:  

.PHONY: all clean

all: epw

epw: epw.h epw.c lexer.o symtab.o syntree.o
	$(CC) -c epw.c
	$(CC) -o epw parser.o lexer.o epw.o symtab.o syntree.o -lfl

lexer.o: epw.l epw.y
	$(YACC) -d --report=all -g --output=parser.c epw.y
	$(LEX) -olexer.c epw.l
	$(CC) -c parser.c lexer.c

symtab.o: symtab.c symtab.h
	$(CC) -c symtab.c

syntree.o: syntree.c syntree.h
	$(CC) -c syntree.c

clean:
	rm -f epw *.o parser.* lexer.c
