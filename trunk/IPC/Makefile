CC = gcc
#CFLAGS = -g -lfl
LEX = flex
YACC = bison

.PHONY: all clean

all: ipc

ipc: ipc.y ipc.l
	$(YACC) --defines --verbose ipc.y
	$(LEX) ipc.l
	$(CC) -o $@ ipc.tab.c lex.yy.c -lfl

clean:
	rm -f ipc *.o lex.yy.c ipc.tab.h ipc.tab.c
