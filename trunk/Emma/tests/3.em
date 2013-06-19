def f(n) {if n==0 return 0 else if n==1 return 1 else return f(n-1)+f(n-2)}

print f(10) # 55
print f(20) # 6765
