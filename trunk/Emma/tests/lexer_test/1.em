# Lexer test
# Skip comments
x_var = 42 ;; ; ; # Skip trailing comment and consecutive ;
# Skip consecutive EOL

_x_var > 42.
; _0_x >= 42
_x_0 == 0.42
_ <= .42
__ < 4.2e20
x != 4e20

x = 4.e20 * y
x = .42e+20 * (x+y)
x = 4.e-20 % x / y - 4.2

# String literals
x = "hello \" world ' "
x = 'hello \' world " '

if (x == 42) {
    y = 4.2;
} else {
    y = 42.
} a = 4.2; b = 0.42
