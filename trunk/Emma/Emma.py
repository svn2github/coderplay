#!/usr/bin/env python
import sys
import specs
import file
from epw_lexer import Lexer, LexError
from epw_parser import parse_file, parse_prompt, ParseError, get_ContinueInput, set_ContinueInput
from epw_ast import EvalError

'''
Emma is a computer language designed to be flexible and easy to use. 
The initial goal is to make the language Turing complete. Additional
features are possible but not required.

ywangd@gmail.com
'''

SETTINGS = [
    ('$DEBUG', 1), 
    ('$PROMPT', 'Emma'),
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
    promptPrefix = topEnv['$PROMPT']

    # Batch file
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        f = open(filename)
        lines = f.readlines()
        f.close()

        tokenlist = []
        for idx in range(len(lines)):
            try:
                tokens_line = lex(file.Line(lines[idx], idx+1, filename))
            except LexError as e:
                sys.stderr.write('%s: %s  (L%d, C%d)\n' % e.args)
                sys.exit(1)
            tokenlist.append(tokens_line)

        print tokenlist

    # REPL
    else:
        line_number = 1
        oldText = '' # Initialize the text input as empty
        while True:

            if promptPrefix == topEnv['$PROMPT']:
                promptString = promptPrefix + ' [%d]> ' % line_number
            else:
                promptString = promptPrefix + '> '

            newText = raw_input(promptString)

            # A single period exits the prompt
            if newText == '.':
                set_ContinueInput(0)
                break

            # Append an EOL at the end of the line since the input from
            # raw_input does not have it and the BNF requires it as the
            # terminator. 
            text = oldText + newText + '\n'

            try:

                # Lexing
                tokenlist = lex(file.Line(text, line_number))
                if topEnv['$DEBUG'] and len(tokenlist) > 1: print tokenlist

                # Parsing
                # We may skip parsing we find any dangling "{" ?
                ast = parse_prompt(tokenlist)

                # Evaluate the AST
                if ast:
                    if topEnv['$DEBUG']: print ast
                    #res = ast.eval(topEnv)
                    #output = res.__repr__()
                    #if output: print output
                    line_number += 1

            except LexError as e:
                sys.stderr.write('%%[LexError]%s: %s  (L%d, C%d)\n' % e.args)
                if topEnv['$DEBUG'] and len(tokenlist) > 1: print tokenlist
                line_number += 1

            except ParseError as e:
                if get_ContinueInput():
                    print 'Continue', tokenlist
                else:
                    sys.stderr.write('%%[ParseError]%s: %s\n' % e.args)
                    if topEnv['$DEBUG'] and len(tokenlist) > 1: print tokenlist
                    line_number += 1

            except EvalError as e:
                sys.stderr.write('%%[EvalError]%s: %s\n' % e.args)
                if topEnv['$DEBUG'] and len(tokenlist) > 1: print tokenlist
                line_number += 1

            finally:
                # if we want continue input, we save the text
                if get_ContinueInput(): 
                    oldText = text
                    set_ContinueInput(0)
                    promptPrefix = '--------'
                else:
                    oldText = ''
                    promptPrefix = topEnv['$PROMPT']



