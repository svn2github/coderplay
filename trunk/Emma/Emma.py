#!/usr/bin/env python
import sys
import random
import specs
import file
from epw_lexer import Lexer, LexError, TokenList
from epw_parser import parse_file, parse_prompt, ParseError
from epw_interpreter import EvalError, BreakControl, ContinueControl, ReturnControl
from epw_env import get_topenv

'''
Emma is a computer language designed moslty for educational purpose.
The basic goal is to make the language Turing complete. Additional
features are possible but not required. 

The Python version is to prototype the possible future C version.
Therefore the coding may not be very pythonic to facilitate the 
subsequent adpation to C.

Features Supported:
    Flow control with if-else, for loops, while loops
    Flow control with break, continue and return
    Functions, return value, recursive calls
    List

Features to be Added:
    Coercion
    Input/Output

Author: ywangd@gmail.com
'''

class Emma(object):

    def __init__(self):
        self.lex = Lexer()
        for token_type in specs.token_type_list:
            self.lex.add_token_type(token_type)
        self.topenv = get_topenv()
        self.topenv.update(specs.SETTINGS)

    def run_repl(self):
        'REPL prompt'
        print self.topenv.get('$NAME') + ' ' + self.topenv.get('$VERSION')
        print 'MoTD: ' + random.choice(self.topenv.get('$MOTD'))
        print
        line_number = 1
        tokenlist = TokenList()
        # Repeat the prompt till user quits
        while True:

            # set up the proper prompt string
            normal_prompt = self.topenv.get('$PROMPT') + ' [%d]>' % line_number
            nident = tokenlist.nLCurly - tokenlist.nRCurly
            if nident == 0:
                promptString = normal_prompt + ' '
            else:
                indent_width = nident * self.topenv.get('$SHIFTWIDTH')
                promptString = self.topenv.get('$PROMPT_CONTINUE')*(len(normal_prompt)+indent_width) + ' '

            # Get input from the prompt
            text = raw_input(promptString)

            # Magic commands for ending the session
            if text == '.exit': break

            # Append an EOL at the end of the line since the input from
            # raw_input does not have it and the BNF requires it as the
            # terminator. 
            text += '\n'
            # Built the character stream
            file_line = file.Line(text, line_number)
            
            # Lexing
            try:
                tokenline = self.lex(file_line)

                # Add to the existing list
                tokenlist.concatenate(tokenline) 
                # If we have unmatched {} pair, don't parsing till all pairs are matched.
                if tokenlist.nLCurly != tokenlist.nRCurly:
                    continue

                if self.topenv.get('$DEBUG') and len(tokenlist) > 1: print tokenlist

            except LexError as e:
                sys.stderr.write('%%[LexError] %s: %s  (L%d, C%d)\n' % e.args)
                if self.topenv.get('$DEBUG') and len(tokenlist) > 1: print tokenlist
                tokenlist.reset()
                continue

            # Parsing
            try:
                ast = parse_prompt(tokenlist)
                if ast and self.topenv.get('$DEBUG'): print ast

            except ParseError as e:
                sys.stderr.write('%%[ParseError] %s: %s\n' % e.args)
                if self.topenv.get('$DEBUG') and len(tokenlist) > 1: print tokenlist
                tokenlist.reset()
                continue
            
            # Evaluation
            try:
                if ast:
                    ret = ast.eval(self.topenv)
                    output = ret.__repr__()
                    if output: print 'Ret:', output
                    line_number += 1

            except EvalError as e:
                sys.stderr.write('%%[EvalError] %s: %s\n' % e.args)
                if self.topenv.get('$DEBUG') and len(tokenlist) > 1: print tokenlist

            except BreakControl as e:
                sys.stderr.write('%%[ControlError] Cannot Break From Top Level\n')

            except ContinueControl as e:
                sys.stderr.write('%%[ControlError] Cannot Continue From Top Level\n')

            except ReturnControl as e:
                sys.stderr.write('%%[ControlError] Cannot Return From Top Level\n')

            finally:
                tokenlist.reset()



    def run_file(self, filename):
        'The batch script'
        f = open(filename)
        text = f.read()
        f.close()
        file_line = file.Line(text, 1, filename)

        # Lexing
        try:
            tokenlist = self.lex(file_line)
            if self.topenv.get('$DEBUG') and len(tokenlist) > 1: print tokenlist

        except LexError as e:
            sys.stderr.write('%%[LexError] %s: %s  (L%d, C%d)\n' % e.args)
            sys.exit(1)

        # Parsing
        try:
            ast = parse_file(tokenlist)
            if ast and self.topenv.get('$DEBUG'): print ast

        except ParseError as e:
            pass

        # Evaluation
        try:
            if ast:
                ast.eval(self.topenv)
                pass
        except EvalError as e:
            pass


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

