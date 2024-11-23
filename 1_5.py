from itertools import product


def main():
    for a in range(2, 2025):
        for b in range(a, 2025):
            if check_gesamt_anzahl_apfelsinen(a, b):
                print(a, b)

def check_gesamt_anzahl_apfelsinen(a, b):
    a_i, b_i = a, b
    sum = 0
    while a_i >= 1 and b_i >= 1 and sum <=2024:
        sum += a_i*b_i
        a_i, b_i = a_i-1, b_i-1
    return sum == 2024

if __name__ == '__main__': main()

# {(2;675);(3;338);(11;34)}