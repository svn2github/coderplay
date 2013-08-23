/*
 * TODO
 * 1. support line continuation
 * 2. Check paired brackets
 * 3.
 */

#include "Emma.h"

EmObject *literalTable;

void init_all(int argc, char **argv) {
    // process command line arguments
    char *filename = NULL;
    FILE *fp = stdin;
    EmObject *ob;

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
    literalTable = newhashobject();
    // Add commonly used literals
    ob = newintobject(1);
    hashobject_insert_by_string(literalTable, "1", ob);
    DECREF(ob);
    ob = newintobject(-1);
    hashobject_insert_by_string(literalTable, "-1", ob);
    DECREF(ob);
    ob = newintobject(0);
    hashobject_insert_by_string(literalTable, "0", ob);
    DECREF(ob);

    ob = newstringobject("*");
    hashobject_insert_by_string(literalTable, "*", ob);
    DECREF(ob);

    hashobject_insert_by_string(literalTable, "null", &nulobj);


    // initialize the lexer
    lexer_init();

    // initialize the VM
    vm_init();
}

void cleanup() {
    lexer_free();
    freeobj(literalTable);
    vm_free();
}

int run_file() {

    Node *ptree;
    AstNode *stree;
    EmCodeObject *co;
    EmObject *retval;

    ptree = parse();
    if (ptree) {
        printtree(ptree);

        stree = ast_from_ptree(ptree);
        printstree(stree);

        co = compile_ast_tree(stree);
        printobj((EmObject *)co, stdout);


        INCREF(&nulobj);
        retval = run_codeobject(co, NULL, &nulobj);


        if (retval)
            DECREF(retval);


        freetree(ptree);
        //printf("almost done.\n");
        freestree(stree);
        //printf("almost done.\n");


    }
    fclose(source.fp);

    return 1;
}

int run_prompt() {

    Node *ptree;
    AstNode *stree;
    EmCodeObject *co;
    Environment *env;
    EmObject *retval;

    env = newenv(vm->topenv);

    while (1) {
        ptree = parse();
        if (ptree) {

            if (ptree->type != MAGIC_COMMAND) {
                // printtree(ptree);

                stree = ast_from_ptree(ptree);

                // printstree(stree);

                co = compile_ast_tree(stree);

                INCREF(&nulobj);
                retval = run_codeobject(co, env, &nulobj);
                DECREF(retval);

                vm_reset_for_prompt();

                freetree(ptree);
                freestree(stree);

            } else { // MAGIC_COMMAND
                printf("got magic command %d\n", CHILD(ptree,0)->type);
                if (NCH(ptree) == 2) {
                    printf("magic command arg = %s\n",
                    CHILD(ptree,1)->lexeme);
                }
                if (CHILD(ptree,0)->type == MCA_EXIT) {
                    freetree(ptree); // release memory before exit
                    break;
                }
                // Always release memory of parse tree
                freetree(ptree);
            }
        }
    }
    env_free(env);

    return 1;
}

int main(int argc, char **argv) {

    init_all(argc, argv);


    if (source.type == SOURCE_TYPE_FILE) {
        run_file();

    } else { // SOURCE_TYPE_PROMPT
        run_prompt();
    }

    //printobj(literalTable, stdout);
    //printf("literalTable = %s\n", tostrobj(literalTable));

    cleanup();

    return 0;
}

