CC = gcc
#CFLAGS = -g -lfl
LEX = flex
YACC = bison

.PHONY: all clean

all: ipc

ipc: lex.yy.o main.o
	$(CC) -g -lfl -o ipc lex.yy.o main.o

main.o: main.c

lex.yy.o: lex.yy.c

lex.yy.c: ipc.l
	$(LEX) ipc.l

clean:
	rm -f ipc *.o lex.yy.c
