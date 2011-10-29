CC = gcc
C_INCLUDE_PATH=/user/local/Cellar/readline/6.2.1/include
LIBRARY_PATH=/user/local/Cellar/readline/6.2.1/lib
LEX = flex
YACC = bison

# Delete the default suffixes
.SUFFIXES:  

.PHONY: all clean

all: epw

epw: epw.h epw.c lexer.o symtab.o syntree.o datatype.o
	$(CC) -g -c epw.c
	$(CC) -lfl -lreadline parser.o lexer.o epw.o symtab.o syntree.o datatype.o -o epw

lexer.o: epw.l epw.y
	$(YACC) -d --report=all -g --output=parser.c epw.y
	$(LEX) -olexer.c epw.l
	$(CC) $(CFLAGS) -g -c parser.c lexer.c 

symtab.o: symtab.c symtab.h
	$(CC) -g -c symtab.c

syntree.o: syntree.c syntree.h
	$(CC) -g -c syntree.c

datatype.o: datatype.c datatype.h
	$(CC) -g -c datatype.c

clean:
	rm -f epw *.o parser.* lexer.c *.*~ core*
