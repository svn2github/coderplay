CC = gcc
#CFLAGS = -g -lfl
LEX = flex
YACC = bison

.PHONY: all clean

all: ipc

ipc: ipc.y ipc.l ipc.c ipc.h
	$(YACC) --defines --verbose ipc.y
	$(LEX) ipc.l
	$(CC) -o $@ ipc.tab.c lex.yy.c ipc.c -lfl

clean:
	rm -f ipc *.o lex.yy.c ipc.tab.h ipc.tab.c ipc.output
