#include "Emma.h"

EmObject *constTable;

int main(int argc, char **argv) {

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
    }

    constTable = newhashobject();

    // parse the input and generate syntax tree
    parse(fp, filename);

    // close the input file
    if (fp != stdin)
        fclose(fp);

    printobj(constTable, stdout);
    freeobj(constTable);

    return 0;
}

