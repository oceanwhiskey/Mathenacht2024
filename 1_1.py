from itertools import product
import math

def main():
    print(24*35)
    coeffs = [6, 31, -570, -2965, 7074, 38349, -21870, -127575]
    a_0 = coeffs[-1]

    nullstellen_kandidaten = positive_und_negative_teiler_von(a_0)
    nullstellen = [x for x in nullstellen_kandidaten if is_nullstelle(coeffs, x)]
    coeffs_reduced = coeffs
    for nullstelle in nullstellen:
        coeffs_reduced, y = horner(coeffs_reduced, nullstelle)
    print(coeffs_reduced) # 6, 1, -35
    # p-q-Formel => -31/6

def horner(coeffs, x):
    reduced_coeffs = [0] * len(coeffs)
    for i in range(len(coeffs)):
        reduced_coeffs[i] = coeffs[i] + (0 if i == 0 else reduced_coeffs[i-1]*x)
    return reduced_coeffs[:-1], reduced_coeffs[-1]

def positive_und_negative_teiler_von(n):
    zahl = abs(n)
    pairs = (f(k) for k in range(1, math.ceil(zahl ** 0.5)) if zahl % k == 0 for f in (identity, lambda x: zahl // x))
    return [f(x) for x in pairs for f in (negate, identity)]

def negate(x):
    return -x

def identity(x):
    return x

def is_nullstelle(coeffs, x):
    _, y = horner(coeffs, x)
    return y == 0



if __name__ == '__main__': main()
