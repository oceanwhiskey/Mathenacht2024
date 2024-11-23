from itertools import product
import math

# Herons Formel: $A=\sqrt{s(s-a)(s-b)(s-c)}$ mit $s=\frac{1}{2}(a+b+c)=\frac{U}{2}$.
# Umformen: $(a+b-c)(a+c-b)(b+c-a)=16(a+b+c)$.

n = 500
eps = 0.00001

def is_flaeche_und_Umfang_gleich(a,b,c):
    U = a+b+c
    s = U/2
    A = (s*(s-a)*(s-b)*(s-c)) ** 0.5
    assert abs(A-U) < eps


for a in range(1, n+1):
    for b in range(a, n+1):
        for c in range(b, n+1):
            if (b+c-a)*(a+c-b)*(a+b-c) == 16*(a+b+c):
                is_flaeche_und_Umfang_gleich(a, b, c)
                print(a, b, c)

# 5 12 13
# 6 8 10
# 6 25 29
# 7 15 20
# 9 10 17                