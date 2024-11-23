def main():
    x = ''.join((str(x) for x in range(1, 51)))
    x = int(x)
    print(quersumme(x))
    res = ''.join(s for s in str(x) if s not in ['9', '8', '7'])
    print(res)
    print(quersumme(int(res)))

def quersumme(n):
    s = 0
    while n:
        s += n % 10
        n //= 10
    return s

if __name__ == '__main__': main()

# 1234561011121314151611120212223242526222303132333435363334041424344454644450
# 4 vorne löschen, 6 hinten
# 1235610111