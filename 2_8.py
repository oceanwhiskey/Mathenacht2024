from itertools import product, repeat
import math

def main():
    print('Lösungen Aufgabe 1:')
    solve_aufgabe_1()

    print()

    print('Lösungen Aufgabe 2:')
    solve_aufgabe_2()
    
    # Aufgabe 3 ist vermutlich ein Scherz!? Kann keine Lösung geben.


def solve_aufgabe_1():
    ub = 19
    for a, b, c in product(range(0, ub+1), range(0, ub+1) ,range(0, ub+1)):
        if aufgabe_1_bedingung(a, b, c):
            print(a, b, c) 

def aufgabe_1_bedingung(a, b, c):
    return a*b + c == 17 and a + b*c == 19

def solve_aufgabe_2():
    for a, b, c in product(range(-16, 17), range(-16, 17), range(-16, 17)):
        if aufgabe_2_bedingung(a, b, c):
            print(a, b, c) 

def aufgabe_2_bedingung(a, b, c):
    return a**abs(b) == 16 and b**abs(c) == 512 and c**abs(a) == 6561


if __name__ == '__main__': main()