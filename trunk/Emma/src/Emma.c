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
    source.type = SOURCE_TYPE_PROMPT;
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
            if (ptree) {

                if (ptree->type != MAGIC_COMMAND) {
                    printtree(ptree);


                } else { // MAGIC_COMMAND
                    printf("got magic command %d\n", CHILD(ptree,0)->type);
                    if (NCH(ptree) == 2)
                        printf("magic command arg = %s\n", CHILD(ptree,1)->lexeme);
                    if (CHILD(ptree,0)->type == MCA_EXIT) {
                        freetree(ptree); // release memory before exit
                        break;
                    }
                }
                // Always release memory
                freetree(ptree);
            }
        }
    }

    printobj(constTable, stdout);
    printf("constTable = %s\n", tostrobj(constTable));

    cleanup();

    return 0;
}

