from itertools import product
import math

# Anzahl, 3 beliebige Punkte zu wählen, davon die abziehen, die auf einer Linie sind
print(math.comb(21, 3) - 2*math.comb(11,3))

limit = 1000

count = 0
for n in range(-limit, limit):
    for m in range(-limit, limit):
        if m**4 + 8*n**2 + 350 == n**4 + 42*m**2 - 75:
            print(m,n)
            count += 1
print(count)



# 1000;16