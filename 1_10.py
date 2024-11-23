import str8ts_solver as solver
import numpy

# Dank an https://gitlab.com/deakandrei/str8ts-solver

def main():
    missing_nums = [solve_and_return_missing_nums(*str8t()) for str8t in (oben_links, oben_rechts, unten_links, unten_rechts)]
    missing_nums = [num for nums in missing_nums for num in nums]
    print(sum(missing_nums)) #320

def oben_links():
    blocked = '''
100011001
000010001
001100100
000001100
100000001
001100000
001001100
100010000
100110001
'''
    hints = '''
600400000
000000609
000050100
100008000
000030000
000000000
002070000
000000400
060000000
'''
    return blocked, hints

def oben_rechts():
    blocked = '''
100000000
010001001
000011001
001100000
011000110
000001100
100110000
100100010
000000001
'''
    hints = '''
000000000
000000002
000090030
090000010
000000070
000200100
350006000
002400060
000900000
'''
    return blocked, hints

def unten_links():
    blocked = '''
000001000
100000000
100010001
000100111
000000000
111001000
100010001
000000001
000100000
'''
    hints = '''
000000000
000000100
608050040
050900003
000002500
041000006
000000000
020008000
000000080
'''
    return blocked, hints

def unten_rechts():
    blocked = '''
110000110
000000000
000100001
000000111
010000010
111000000
100001000
000000000
011000011
'''
    hints = '''
000050000
008720050
600900000
000600000
000000000
021000000
003000006
000007480
000000003
'''
    return blocked, hints


def solve_and_return_missing_nums(blocked: str, hints):
    blocked_array = read_string_block_to_int_array(blocked)
    hints_array = read_string_block_to_int_array(hints)
    config = numpy.asarray([blocked_array, hints_array])
    
    B = solver.Board(config)
    B = solver.depth_first_search(B)

    missing_nums = [missing_nums_from_1_to_9_in_column(col) for col in B.cols]
    missing_nums = [x for y in missing_nums for x in y]
    return missing_nums

def read_string_block_to_int_array(block):
    return [split_row_to_list_of_ints(row) for row in block.strip().split()]    

def split_row_to_list_of_ints(row):
    return [int(c) for c in row]

def transf(l):
    return [int(x) for x in l]

def missing_nums_from_1_to_9_in_column(col):
    nums = set(range(1,10))
    for field in (x.candidates for x in col):
        if field != 0:
            nums.remove(field)
    return nums


if __name__ == '__main__': main()