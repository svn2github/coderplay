CC = gcc
#CFLAGS = -g -lfl
LEX = flex
YACC = bison

.PHONY: all clean

all: ipc

ipc: lex.yy.o ipc.tab.o
	$(CC) -lfl -o ipc lex.yy.o ipc.tab.o

ipc.tab.o: ipc.tab.c

lex.yy.o: lex.yy.c

lex.yy.c: ipc.l
	$(LEX) ipc.l

ipc.tab.c: ipc.y
	$(YACC) -d ipc.y

clean:
	rm -f ipc *.o lex.yy.c
