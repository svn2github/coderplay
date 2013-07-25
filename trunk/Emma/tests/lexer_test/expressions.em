# Experession and identifiers
# Skip consecutive EOLs

_x1 = -x2 + x3 - x4 * x5 / x6 % x7

; x1 = (x2 + x3) ** x4 # ignore leading semicolon and trailing comment
# Logical operations
x1 = not x2<x3 and x3 > x4 or x4 <= x5 xor x5 >= x6 and x6 == x7 and x7!=x8

# function call
func(x, y) ;; ;; ; # consecutive semicolons are treat as a single one

# array element
array(x)
