CC = gcc
LEX = flex
YACC = bison
MV = mv -f 

# Delete the default suffixes
.SUFFIXES:  

.PHONY: all clean

all: ipc

ipc: ipc.h ipc.c lexer.o
	$(CC) -c ipc.c
	$(CC) -o ipc parser.o lexer.o ipc.o -lfl

lexer.o: ipc.l ipc.y
	$(YACC) -d --report=all -g --output=parser.c ipc.y
	$(LEX) ipc.l
	$(MV) lex.yy.c lexer.c
	$(CC) -c parser.c lexer.c

clean:
	rm -f ipc *.o parser.* lexer.c
