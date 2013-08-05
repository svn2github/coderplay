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
    // parse the input and generate parse tree
    if (source.type == SOURCE_TYPE_PROMPT) {
        ptree = parse_prompt_input();
    } else if (source.type == SOURCE_TYPE_FILE) {
        ptree = parse_file_input();
    }

    // release the tree
    freetree(ptree);

    // close the input file
    if (source.fp != stdin)
        fclose(source.fp);

    printobj(constTable, stdout);
    printf("constTable = %s\n", tostrobj(constTable));


    cleanup();

    return 0;
}




