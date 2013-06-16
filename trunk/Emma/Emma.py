#!/usr/bin/env python
import sys
import specs
import file
from epw_lexer import Lexer, LexError
from epw_parser import parse_file, parse_prompt
from epw_ast import EvalError

'''
Emma is a computer language designed to be flexible and easy to use. 
The initial goal is to make the language Turing complete. Additional
features are possible but not required.

ywangd@gmail.com
'''

SETTINGS = [
    ('$DEBUG', 1), 
]


class Environment(dict):
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, name):
        'Find the innermost Environment where name exists'
        if name in self:
            return self
        else:
            if self.outer is not None:
                return self.outer.find(name)
            else:
                return None
    def top(self):
        if self.outer is not None:
            return self.outer.top()
        else:
            return self

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

    # Prepare the Environment
    topEnv = Environment()
    topEnv.update(SETTINGS)

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
                # append an EOL at the end of the line since the input from
                # raw_input does not have it and the BNF requires it as the
                # terminator. 
                text += '\n'
                tokens = lex(file.Line(text, line_number))
                if topEnv['$DEBUG'] and len(tokens) > 1: print tokens
                ast = parse_prompt(tokens)
                # Evaluate the AST
                if ast:
                    if topEnv['$DEBUG']: print ast
                    #res = ast.eval(topEnv)
                    #output = res.__repr__()
                    #if output: print output
                    line_number += 1

            except LexError as e:
                sys.stderr.write('%%%s: %s  (L%d, C%d)\n' % e.args)
                line_number += 1

            except EvalError as e:
                sys.stderr.write('%%%s: %s\n' % e.args)
                line_number += 1


