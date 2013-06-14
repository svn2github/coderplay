#!/usr/bin/env python
import sys
import specs
import file
from lexer import Lexer, LexError
from epw_parser import parse_file

'''
Emma is a computer language designed to be flexible and easy to use. 

ywangd@gmail.com
'''

def usage(prog):
    sys.stderr.write('usage: %s filename\n' % prog)
    sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) > 2:
        usage(sys.argv[0])

    # Initialize the Lexer
    lex = Lexer()
    for token_type in specs.token_type_list:
        lex.add_token_type(token_type)

    # Batch file
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        f = open(filename)
        lines = f.readlines()
        f.close()

        tokens_list = []
        for idx in range(len(lines)):
            try:
                tokens = lex(file.Line(lines[idx], idx+1, filename))
            except LexError as e:
                sys.stderr.write('%s: %s  (L%d, C%d)\n' % e.args)
                sys.exit(1)
            tokens_list.append(tokens)

        print tokens_list

    # REPL
    else:
        line_number = 1
        while True:
            text = raw_input('Emma [%d]> ' % line_number)

            if text == '.':
                break

            try:
                tokens = lex(file.Line(text, line_number))
                if len(tokens):
                    line_number += 1
                    print tokens
                    ast = parse_file(tokens)
                    print ast

            except LexError as e:
                sys.stderr.write('%%%s: %s  (L%d, C%d)\n' % e.args)
                line_number += 1






