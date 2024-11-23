from itertools import product
import math

def main():
    ermittle_d1() # 101, Q(d1) = 2
    ermittle_d2() # 52, Q(d2) = 7
    ermittle_d3() # 135, Q(d3) = 9

 # Es folgt x=6.

    x = ((14**0.5 - 63**0.5)/(2**0.5 - 9**0.5)) ** 2
    print(x)

def ermittle_d1():
    for d1 in (x for x in range(51, 1000) if x % 2 == 1):
        if(f(f(d1))) == 26:
            print(d1)

def ermittle_d2():
    for d2 in range(51, 1000):
        if g(g(g(g(g(d2))))) == 44:
            print(d2)

def ermittle_d3():
    for d3 in (x for x in range(51, 1000) if x % 2 == 1):
        if h(h(h(d3))) == 35:
            print(d3)    

def f(n):
    if n % 2 == 0:
        return n+3
    return (n+1) // 2

def g(n):
    rest = n % 3
    if rest == 0:
        return n-3
    if rest == 1:
        return n-2
    if rest == 2:
        return n-1

def h(n):
    if n % 2 == 0:
        return n // 2
    return n+5




if __name__ == '__main__': main()