import sys
from bob.bobparser import *
from bob.compiler import BobCompiler, BobAssembler
from bob.vm import BobVM


if __name__ == "__main__":
    filename = sys.argv[1]
    s = open(filename).read()
    print s

    parser = BobParser()
    compiler = BobCompiler()

    print '---------------------------'
    print 'parsing'
    print '---------------------------'
    parsed = parser.parse(s)
    print parsed

    print '---------------------------'
    print 'compiling'
    print '---------------------------'
    compiled = compiler.compile(parsed)
    print compiled

    print '---------------------------'
    print 'assembling'
    print '---------------------------'
    assembled = BobAssembler().assemble(compiled)
    print assembled

    #vm = BobVM()
    #vm.run(assembled)

