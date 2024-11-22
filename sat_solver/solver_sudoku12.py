from sat_utils import solve_one, one_of, basic_fact, itersolve
from sys import intern
from pprint import pprint

n = 4

grid = '''\
AA AB AC AD AE AF AG AH AI AJ AK GA
BA BB BC EA EB EC ED EE EF AL GB GC
BD CA BE BF EG EH EI EJ EK GD GE GF
CB CC CD BG BH BI FA EL FB GG GH GI
CE CF BJ BK FC FD FE FF FG GJ GK HA 
CG CH CI BL FH FI FJ KA FK HB GL HC 
CJ DA CK KB FL KC KD KE LA HD HE HF
CL DB DC KF KG KH KI KJ LB LC HG HH
DD DE DF KK JA KL LD LE LF HI HJ HK
DG DH DI JB JC JD JE JF LG LH HL LI
DJ DK IA JG JH JI JJ JK JL LJ LK LL
DL IB IC ID IE IF IG IH II IJ IK IL
'''

values = list('123456789ABC')

table = [row.split() for row in grid.splitlines()]
points = grid.split()
subsquares: dict = dict()
for point in points:
    subsquares.setdefault(point[0], []).append(point)
# Groups:  rows   + columns           + subsquares    
groups = table[:] + list(zip(*table)) + list(subsquares.values())
# print(groups)
print(subsquares)


del grid, subsquares, table     # analysis requires only:  points, values, groups

def comb(point, value):
    'Format a fact (a value assigned to a given point)'
    return intern(f'{point} {value}')

def str_to_facts(s):
    'Convert str in row major form to a list of facts'
    return [comb(point, value) for point, value in zip(points, s) if value != ' ']

def facts_to_str(facts):
    'Convert a list of facts to a string in row major order with blanks for unknowns'
    point_to_value = dict(map(str.split, facts))
    return ''.join(point_to_value.get(point, ' ') for point in points)

def show(flatline):
    'Display grid from a string (values in row major order with blanks for unknowns)'
    fmt = '|'.join(['%s' * n] * n)
    sep = '+'.join(['-'  * n] * n)
    for i in range(n):
        for j in range(n):
            offset = (i * n + j) * n**2
            print(fmt % tuple(flatline[offset:offset+n**2]))
        if i != n - 1:
            print(sep)

def show2(string, length):
    gs = [string[0 + i:length + i] for i in range(0, len(string), length)]
    for g in gs:
        print(g)

for given in [
    'A  9   8 B 7 C    8     8 564  1   2    2    96  5   2 9    1  4   75 B  1 58   B  C    B 1   4  87    2    6   A  538 9     8    A B 2 C   8  6'
    ]:
    cnf: list = []

    # each point assigned exactly one value
    for point in points:
        cnf += one_of(comb(point, value) for value in values)

    # each value gets assigned to exactly one point in each group
    for group in groups:
        for value in values:
            cnf += one_of(comb(point, value) for point in group)

    # add facts for known values in a specific puzzle
    for known in str_to_facts(given):
        cnf += basic_fact(known)

    # solve it and display the results
    show2(given, 12)
    results = itersolve(cnf)
    for result in results:
        print('=-' * 20)
        show2(facts_to_str(result), 12)
        