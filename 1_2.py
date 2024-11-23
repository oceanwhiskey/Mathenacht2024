import math

def main():
    zwoelf_fakultaet = 479001600
    for x in range(zwoelf_fakultaet + 13, 2*zwoelf_fakultaet):
        if is_prime(x):
            print(x-zwoelf_fakultaet-1)
            break

def is_prime(n):
    for k in range(2, math.ceil(n ** 0.5)):
        if n % k == 0:
            return False
    return True

if __name__ == '__main__': main()