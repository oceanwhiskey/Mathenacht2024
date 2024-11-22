from sat_utils import solve_one, from_dnf, one_of, itersolve
from sys import intern
from pprint import pprint
import itertools

houses =     ['1',          '2',      '3',           '4',         '5'       ]

groups = [
             ['Journalist','IT-Berater','Lehrer',   'Kapitän zur See', 'Ingenieur'   ],
             ['Polen',    'Niederlande',    'Ungarn',       'Deutschland',     'Irland'     ],
             ['21',     '24',    '32',        '40',      '52'      ],
             ['Handball',     'Schwimmen',    'Volleyball',        'Leichtathletik',    'Fußball'],
             ['Greifswald', 'Magdeburg', 'Potsdam', 'An der Müritz',   'Rostock'   ],
]

values = [value for group in groups for value in group]

def comb(value, house):
    'Format how a value is shown at a given house'
    return intern(f'{value} {house}')

def found_at(value, house):
    'Value known to be at a specific house'
    return [(comb(value, house),)]

def same_house(value1, value2):
    'The two values occur in the same house:  brit1 & red1 | brit2 & red2 ...'
    return from_dnf([(comb(value1, i), comb(value2, i)) for i in houses])

def consecutive(value1, value2):
    'The values are in consecutive houses:  green1 & white2 | green2 & white3 ...'
    return from_dnf([(comb(value1, i), comb(value2, j))
                     for i, j in zip(houses, houses[1:])])

def beside(value1, value2):
    'The values occur side-by-side: blends1 & cat2 | blends2 & cat1 ...'
    return from_dnf([(comb(value1, i), comb(value2, j))
                     for i, j in zip(houses, houses[1:])] +
                    [(comb(value2, i), comb(value1, j))
                     for i, j in zip(houses, houses[1:])]
                    )

def beside_age_diff(house1, house2, group, diff):
    'The values occur side-by-side: blends1 & cat2 | blends2 & cat1 ...'
    diffs = [x for x in itertools.combinations(group, 2) if abs(int(x[0]) - int(x[1])) == diff]
    return from_dnf([(comb(x, house1), comb(y, house2)) for x,y in diffs] + [(comb(x, house2), comb(y, house1)) for x,y in diffs])

cnf = []

# each house gets exactly one value from each attribute group
for house in houses:
    for group in groups:
        cnf += one_of(comb(value, house) for value in group)

# each value gets assigned to exactly one house
for value in values:
    cnf += one_of(comb(value, house) for house in houses)

cnf += found_at('Ingenieur', 1)
cnf += found_at('Volleyball', 3)
cnf += same_house('Polen', 'Journalist')
# cnf += same_house('IT-Berater', '21')
cnf += same_house('Lehrer', 'Schwimmen')
cnf += same_house('Kapitän zur See', 'Rostock')
cnf += same_house('Handball', 'Niederlande')
cnf += same_house('Irland', 'Magdeburg')
# cnf += same_house('Greifswald', '32')
cnf += same_house('Leichtathletik', 'An der Müritz')
cnf += beside('Niederlande', 'Ungarn')
# cnf += beside('52', 'Potsdam')
# cnf += beside('24', 'Magdeburg')
cnf += beside('Ingenieur', 'Deutschland')
cnf += beside_age_diff(2, 3, groups[2], 8)
cnf += beside_age_diff(4, 5, groups[2], 19)
cnf += beside_age_diff(1, 2, groups[2], 20)
cnf += found_at('IT-Berater', 5)

sols = itersolve(cnf)
for sol in sols:
    pprint(sol)
# pprint(solve_one(cnf))

# print(beside_age_diff(1, 2, groups[2], 8))
