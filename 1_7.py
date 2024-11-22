from itertools import product
n = 30000

for h in range(0, n):
    for s in range(h, n):
        s2 = s*s
        h2 = h*h
        if 9*s2 == (s2-h2)*h2:
            print(s, h)