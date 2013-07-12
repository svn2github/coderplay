#!/usr/bin/env python
import sys
import random
from pprint import pprint
import specs
from file import Lines
from epw_lexer import Lexer, LexError, TokenList
from epw_parser2 import parse_file, parse_prompt, ParseError
from epw_interpreter import EvalError, BreakControl, ContinueControl, ReturnControl
from epw_env import get_topenv
from epw_compiler import Compiler
from epw_vm import VM, VMError
from epw_assembler import assemble


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
    Line continuation character

Author: ywangd@gmail.com
'''

class Emma(object):

    def __init__(self):
        self.lex = Lexer()
        self.compiler = Compiler()
        self.vm = VM()
        for token_type in specs.token_type_list:
            self.lex.add_token_type(token_type)
        self.topenv = get_topenv()
        self.topenv.update(specs.SETTINGS)

    def tidy(self):
        self.topenv.binding.clear()

    def run_repl(self):
        'REPL prompt'
        print self.topenv.get('$NAME') + ' ' + self.topenv.get('$VERSION')
        print 'MoTD: ' + random.choice(self.topenv.get('$MOTD'))
        print

        line_number = 1
        tokenlist = TokenList()
        lines = Lines()

        # Repeat the prompt till user quits
        while True:

            # set up the proper prompt string
            normal_prompt = self.topenv.get('$PROMPT') + ' [%d]>' % line_number
            nident = tokenlist.nLCurly - tokenlist.nRCurly
            if nident == 0:
                promptString = normal_prompt + ' '
            else:
                indent_width = nident * self.topenv.get('$SHIFTWIDTH')
                promptString = self.topenv.get('$PROMPT_CONTINUE') \
                               * (len(normal_prompt)+indent_width) + ' '

            # Get input from the prompt
            text = raw_input(promptString)

            if text == '': continue
            # Magic commands 
            if text[0] == '.':
                if text == '.exit': break
                fields = text.split(' ')
                if fields[0] == '.run':
                    filename = text[4:].strip()
                    if filename != '':
                        if self.run_file(filename):
                            line_number +=1
                    continue

            # Append an EOL at the end of the line since the input from
            # raw_input does not have it and the BNF requires it as the
            # terminator. 
            text += '\n'
            # prefix with whitespaces for multiple line input, so the 
            # error message looks better with the indentation.
            if nident != 0:
                text = indent_width * ' ' + text

            # Built the character stream
            lines.append(text)

            # Process the stream
            if self.process_file_line(1, lines, tokenlist):
                line_number += 1


    def process_file_line(self, isPrompt, lines, tokenlist=None):
        'The core processing'    
        # Lexing
        try:
            tokenline = self.lex(lines)

            # save the input lines in the top env 
            self.topenv.set('$INPUT_LINES', lines)

            # Add to the existing list if any
            if tokenlist is not None:
                tokenlist.concatenate(tokenline) 
            else:
                tokenlist = tokenline

            # If we have unmatched {} pair, don't parsing till all pairs are matched.
            if isPrompt and tokenlist.nLCurly != tokenlist.nRCurly:
                return

            if self.topenv.get('$DEBUG'): print tokenlist

        except LexError as e:
            sys.stderr.write(repr(e))
            if self.topenv.get('$DEBUG'): print tokenlist
            lines.reset()
            tokenlist.reset()
            return

        # Parsing
        try:
            if isPrompt:
                parsed = parse_prompt(tokenlist)
            else:
                parsed = parse_file(tokenlist)
            if parsed and self.topenv.get('$DEBUG'): print parsed

        except ParseError as e:
            sys.stderr.write(repr(e))
            if self.topenv.get('$DEBUG'): print tokenlist
            lines.reset()
            tokenlist.reset()
            return

        # Compilation
        compiled = self.compiler.compile(parsed)
        print compiled

        # Assembling
        assembled = assemble(compiled)
        print assembled
        
        # Evaluation
        try:
            self.vm.run(assembled)

        except VMError as e:
            sys.stderr.write(repr(e))
            if self.topenv.get('$DEBUG'): print tokenlist
            lines.reset()
            tokenlist.reset()
            return

        # Everything is fine if we reach here
        lines.reset()
        tokenlist.reset()
        return 1


    def run_file(self, filename):
        'The batch script'
        # Read the source file
        try:
            f = open(filename)
            text = f.readlines()
            f.close()
        except IOError as e:
            sys.stderr.write('%%[IOError] File Not Found: \"%s\"\n' % filename)
            return 0

        lines = Lines()
        for oneline in text:
            lines.append(oneline)

        # Process the content
        if self.process_file_line(0, lines):
            return 1
        else:
            return 0


def usage(prog):
    sys.stderr.write('usage: %s filename\n' % prog)
    sys.exit(0)


def main():
    if len(sys.argv) > 2:
        usage(sys.argv[0])

    emma = Emma()
    if len(sys.argv) == 1:
        emma.run_repl()
    else:
        emma.run_file(sys.argv[1])

    # clear the environment, so it does not contaminate next run
    emma.tidy()


if __name__ == '__main__':
    main()

