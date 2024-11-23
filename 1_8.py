import math
from itertools import combinations, permutations

def main():
    erste_aufgabe() # 20
    zweite_aufgabe() # 4! = 24
    dritte_aufgabe() # 2
    
    #20;24;2/1

def erste_aufgabe():
    # 3 aus 5 ohne Reihenfolge, die größte in der Mitte, die außen können vertauscht werden
    print(2* math.comb(5, 3))

def zweite_aufgabe():
    # { 1, 3, 6, 254 } betrachten, 4! Möglichkeiten.
    # Zur Sicherheit:

    count = 0
    sets = (s for s in permutations(range(1,7)))
    for s in sets:
        if check_254(s):
            count += 1
    print(count)

def check_254(a):
    for i in range(0,4):
        if a[i] == 2 and a[i+1] == 5 and a[i+2] == 4:
            return True
    return False

def dritte_aufgabe():
    count = 0
    sets = (s for s in permutations(range(1,9)))
    for s in sets:
        count += count_spitzen(s)
    print(count/40320)
    
def count_spitzen(a):
    count = 0
    for i, x in enumerate(a):
        if 0 < i < len(a)-1:
            if x > a[i-1] and x > a[i+1]:
                count += 1
    return count


if __name__ == '__main__': main()