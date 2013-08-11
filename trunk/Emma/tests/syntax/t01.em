package foo
import foo.bar.*
try {} catch (a,b) {}
try {} catch (a,b) {} finally {}
try {} catch (a,b) {} catch (e,f) {} finally {}
for i=1,10 {}
for i=1,10,2 print i
if 1 1
if 1 1 else 2
if 1 1 elif 2 2 elif 3 3
if 1 1 elif 2 2 elif 3 3 else 4
class A() {
    def f() {}
    def f(**c) {}
    def f(*b) {}
    def f(*b, **c) {}
    def f(a) {}
    def f(a, *b, **c) {}
    def f(a, *b) {}
    def f(a, **c) {}
}
class A(B) {}
raise
raise ex
print 1, 2
print >outs 1, 2, 2+3
a = f() + 1 * f(a)
f(a, b, c, d=1, e=2)
f(g(),b=a[1])()[:][::][1:][10:0:-1][:10:][::2][3,5,7,11]
