/*
 * TODO
 * 1. support line continuation
 * 2. Check paired brackets
 * 3.
 */

#include "Emma.h"

EmObject *constTable;

int init_all(int argc, char **argv) {
    // process command line arguments
    char *filename = NULL;
    FILE *fp = stdin;

    if (argc > 1)
        filename = argv[1];

    if (filename != NULL) {
        if ((fp = fopen(filename, "r")) == NULL) {
            fprintf(stderr, "Cannot open file %s\n", filename);
            exit(1);
        }
        source.type = SOURCE_TYPE_FILE;
    } else {
        source.type = SOURCE_TYPE_PROMPT;
    }
    source.filename = filename;
    source.fp = fp;

    // Constant hash table
    constTable = newhashobject();

    // initialize the lexer
    lexer_init();
}

int cleanup() {
    lexer_free();
    freeobj(constTable);
}

int main(int argc, char **argv) {

    init_all(argc, argv);

    Node *ptree;

    /*
     * Parse the input
     */
    if (source.type == SOURCE_TYPE_FILE) {
        ptree = parse();
        if (ptree) {
            printtree(ptree);
            freetree(ptree);
        }
        fclose(source.fp);
    } else { // SOURCE_TYPE_PROMPT
        while (1) {
            ptree = parse();
            if (source.promptStatus != MAGIC_NONE) {
                freetree(ptree);
                ptree = NULL;
                if (source.promptStatus == MAGIC_EXIT) {
                    break;
                }
                else if (source.promptStatus == MAGIC_ERROR) {
                    fprintf(stderr, "Error: unknown magic command\n");
                }
                source.promptStatus = MAGIC_NONE;
                source.pos = strlen(source.line);
            }
            if (ptree) {
                printtree(ptree);
                freetree(ptree);
            }
        }
    }

    printobj(constTable, stdout);
    printf("constTable = %s\n", tostrobj(constTable));

    cleanup();

    return 0;
}

