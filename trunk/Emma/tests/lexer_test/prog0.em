# Calcualte Fibonacci series
def f(n) {
    if n==0 return 0 else if n==1 return 1 else return f(n-1)+f(n-2)
}

def f(n) {
    if n == 0 {
        return 0;
    } elif n == 1 {
        return 1
    } else return f(n-1) + f(n-2)
}

# A non-recursive implementation
def f(n) {
    x = list(n+1)
    for i = 0, n, 1 {
        if i == 0 x[i] = 0 elif i == 1 x[i] = 1 else {
            x[i] = x[i-1] + x[i-2];
        }
    }
    return x[n]
}

# recursive class methods
class Fibo() {

    def f(n) {
        if n == 0 return 0;
        if n == 1 return 1;
        return Fibo.f(n-1) + Fibo.f(n-2)
    }

}
