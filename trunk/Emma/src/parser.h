#ifndef _PARSER_H
#define _PARSER_H

#include "node.h"

#define FILE_INPUT          256
#define PROMPT_INPUT        257
#define STRING_INPUT        258
#define STATEMENT           259



Node *parse_file();
Node *parse_prompt();
Node *parse_string();

Node *parse_statement();
Node *parse_stmt();

Node *parse_simple_stmt();

Node *parse_expression();
Node *parse_print_stmt();
Node *parse_read_stmt();
Node *parse_assign_stmt();
Node *parse_continue_stmt();
Node *parse_break_stmt();
Node *parse_return_stmt();
Node *parse_package_stmt();
Node *parse_import_stmt();

Node *parse_compound_stmt();

Node *parse_if_stmt();
Node *parse_while_stmt();
Node *parse_for_stmt();
Node *parse_funcdef();
Node *parse_classdef();
Node *parse_try_stmt();

Node *parse_catch();
Node *parse_finally();

Node *parse_suite();

Node *parse_stmt_block();





Node *parse();


#endif

