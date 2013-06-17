#!/usr/bin/env python
import sys
import random
import specs
import file
from epw_lexer import Lexer, LexError, TokenList
from epw_parser import parse_file, parse_prompt, ParseError
from epw_ast import EvalError
from epw_env import Environment

'''
Emma is a computer language designed to be flexible and easy to use. 
The initial goal is to make the language Turing complete. Additional
features are possible but not required.

ywangd@gmail.com
'''

class Emma(object):

    def __init__(self):
        self.lex = Lexer()
        for token_type in specs.token_type_list:
            self.lex.add_token_type(token_type)
        self.topEnv = Environment()
        self.topEnv.update(specs.SETTINGS)

    def run_repl(self):
        'REPL prompt'
        print self.topEnv['$NAME'] + ' ' + self.topEnv['$VERSION']
        print 'MoTD: ' + random.choice(self.topEnv['$MOTD'])
        print
        line_number = 1
        tokenlist = TokenList()
        # Repeat the prompt till user quits
        while True:

            # set up the proper prompt string
            normal_prompt = self.topEnv['$PROMPT'] + ' [%d]>' % line_number
            nident = tokenlist.nLCurly - tokenlist.nRCurly
            if nident == 0:
                promptString = normal_prompt + ' '
            else:
                indent_width = nident * self.topEnv['$SHIFTWIDTH']
                promptString = self.topEnv['$PROMPT_CONTINUE']*(len(normal_prompt)+indent_width) + ' '

            # Get input from the prompt
            text = raw_input(promptString)

            # A single period exits the prompt
            if text == '.': break

            # Append an EOL at the end of the line since the input from
            # raw_input does not have it and the BNF requires it as the
            # terminator. 
            text += '\n'
            
            # Lexing
            try:
                tokenline = self.lex(file.Line(text, line_number))

                # Add to the existing list
                tokenlist.concatenate(tokenline) 
                # If we have unmatched {} pair, don't parsing till all pairs are matched.
                if tokenlist.nLCurly != tokenlist.nRCurly:
                    continue

                if self.topEnv['$DEBUG'] and len(tokenlist) > 1: print tokenlist

            except LexError as e:
                sys.stderr.write('%%[LexError] %s: %s  (L%d, C%d)\n' % e.args)
                if self.topEnv['$DEBUG'] and len(tokenlist) > 1: print tokenlist
                tokenlist.reset()
                continue

            # Parsing
            try:
                ast = parse_prompt(tokenlist)
                if ast and self.topEnv['$DEBUG']: print ast

            except ParseError as e:
                sys.stderr.write('%%[ParseError] %s: %s\n' % e.args)
                if self.topEnv['$DEBUG'] and len(tokenlist) > 1: print tokenlist
                tokenlist.reset()
                continue
            
            # Evaluation
            try:
                if ast:
                    #res = ast.eval(self.topEnv)
                    #output = res.__repr__()
                    #if output: print output
                    line_number += 1
                    pass

            except EvalError as e:
                sys.stderr.write('%%[EvalError] %s: %s\n' % e.args)
                if self.topEnv['$DEBUG'] and len(tokenlist) > 1: print tokenlist

            finally:
                tokenlist.reset()


    def run_file(self, filename):
        'The batch script'
        f = open(filename)
        lines = f.readlines()
        f.close()

        tokenlist = []
        for idx in range(len(lines)):
            try:
                tokenline = lex(file.Line(lines[idx], idx+1, filename))
            except LexError as e:
                sys.stderr.write('%s: %s  (L%d, C%d)\n' % e.args)
                sys.exit(1)
            tokenlist.append(tokenline)

        print tokenlist



def usage(prog):
    sys.stderr.write('usage: %s filename\n' % prog)
    sys.exit(0)

if __name__ == '__main__':

    if len(sys.argv) > 2:
        usage(sys.argv[0])

    emma = Emma()
    if len(sys.argv) == 1:
        emma.run_repl()
    else:
        emma.run_file(sys.argv[1])

    sys.exit(0)

