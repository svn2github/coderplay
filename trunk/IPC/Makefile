CC = gcc
LEX = flex
YACC = bison

# Delete the default suffixes
.SUFFIXES:  

.PHONY: all clean

all: ipc

ipc: ipc.y ipc.l ipc.h ipc.c
	$(YACC) -d ipc.y
	$(LEX) ipc.l
	$(CC) -o ipc ipc.tab.c lex.yy.c ipc.c -lfl

clean:
	rm -f ipc *.o lex.yy.c ipc.tab.h ipc.tab.c ipc.output
