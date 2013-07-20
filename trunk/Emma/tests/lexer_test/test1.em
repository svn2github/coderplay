# Lexer test 
# NOTE test
# Skip comments
package lexer_test
import lexer_test.test1
x_var = 42 ;; ; ; # Skip trailing comment and consecutive ;
# Skip consecutive EOL

_x_var > 42.
; _0_x >= 42 # leading ; will be ignored
_x_0 == 0.42
_ <= .42
__ < 4.2e20
x != 4e20

x = 4.e20 * y
x = .42e+20 * (x+y)
x = 4.e-20 % x / y - 4.2

a = -b + c * (d-e**f) % g / h

# String literals
x = "hello \" world ' "
x = 'hello \' world " '

print 'hello world!'

if (x == 42 and y == 4.2) {
    y = 4.2;
} else {
    y = 42.
} a = 4.2; b = 0.42 # a semicolon is not required after }

class A() {
    self.field = 42
}

def func(x, y) {
    print x, y
} ; x = 42 # a semiclon can appear after the }

x = list()
