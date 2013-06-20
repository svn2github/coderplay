a = list(5)
b = list(5)
c = list(5)

a[1] = b
a[1][2] = c

def f(n) {if n==0 return 0 else if n==1 return 1 else return f(n-1)+f(n-2)}

a[1][2][3] = f

print a[1][2][3](10)

if f(20) == a[1][2][3](20) print '1' else print '0'

def g() { return a }

print g()[1][2][3](10)

g()[1][2][4] = 99

if a[1][2][4] == 99 print 1 else print 0



