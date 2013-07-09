import sys
from bob.compiler import compile_code
from bob.vm import BobVM


if __name__ == "__main__":
    filename = sys.argv[1]
    s = open(filename).read()
    print s
    co = compile_code(s)
    print co

    vm = BobVM()
    vm.run(co)

