import numpy as np
from collections import Counter as multiset

class NoSolutionPossible(Exception):
    def __init__(self, cause):
        super().__init__(cause)

class Hook:
    # manages calling a list of hooks with the same argument
    def __init__(self, *args):
        self._hooks = list(args)

    def add(self, *args):
        self._hooks.extend(args)
    
    def __call__(self, **kwargs):
        for f in self._hooks:
            f(**kwargs)

class Cell:
    def __init__(self, **kwargs):
        possible = kwargs.get('candidates')
        if possible is not None:
            if type(possible) is int:
                self._possible = { possible }
            else:
                self._possible = possible
        else:
            size = kwargs.get('size')
            if size is None:
                raise ValueError('Both candidates and size arguments were None.')
            self._possible = { i for i in range(1, size+1) }
        self.pos = kwargs.get('pos')
        self.hook = Hook() # Can't copy the same hooks

    @property
    def candidates(self):
        return self._possible

    @candidates.setter
    def candidates(self, value):
        if type(value) is int:
            self._possible = { value }
        else:
            self._possible = value
        self.hook(cell = self)

    @candidates.getter
    def candidates(self):
        if len(self._possible) == 1:
            return next(iter(self._possible))
        return self._possible
    
    def remove_candidates(self, digits):
        common = self._possible.intersection(digits)
        if len(common) != 0:
            self._possible.difference_update(common)
            if len(self._possible) == 0:
                raise NoSolutionPossible('Cell has no possible candidates remaining.')
            # and also call our hook(s)
            self.hook(cell = self)

    def is_solved(self):
        return len(self._possible) == 1

    def has_candidates(self):
        return len(self._possible) > 1

    def copy(self):
        return Cell(candidates = self._possible.copy(), pos = self.pos)
    
    def __iter__(self):
        return iter(self._possible)
    
    def __len__(self):
        return len(self._possible)
    
    def __getitem__(self, key):
        return self.pos[key]
    
    def __repr__(self):
        if self.is_solved():
            return str(self.candidates)
        mat = self.matrix_repr()
        string = '\n'
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                if mat[i][j] == 0:
                    string += ' '
                else:
                    string += str(mat[i][j])
            string += '\n'
        return string
    
    def matrix_repr(self):
        ret = np.zeros((3, 3), dtype = object)
        if self.is_solved():
            ret[1][1] = self.candidates
        else:
            for i in self._possible:
                lin = (i-1) // 3
                col = (i-1) % 3
                ret[lin][col] = i
        return ret

def non_void_union(sets):
    res = multiset()
    for s in sets:
        if len(s) == 0:
            return multiset()
        res.update(s)
    return res

class CellGroup:
    # A class to manage groups of continuous cells (pieces of a line or column)
    def __init__(self, cells, hook = None):
        self.cells = tuple(cells) # the cells that make this group
        self._unsolved = { cell.pos : cell for cell in self.cells if not cell.is_solved() } # the list of yet unsolved cells
        self._to_elliminate = set() # cell positions to be elliminated from _unsolved
        self.changed = True # true if this group has changed in the meantime
        self.hook = hook if hook is not None else Hook()
        # and don't forget to hook up the cells to our cell_changed() method
        for cell in self.cells:
            cell.hook.add(self._cell_changed)

    @property
    def unsolved(self):
        return self._unsolved.values()

    def _cell_changed(self, cell):
        # this is called by a cell if it was changed
        self.changed = True
        if cell.is_solved():
            self._to_elliminate.add(cell.pos)
        # call our hook
        self.hook(compartment = self)

    def propagate(self, digits, exept = None):
        # removes candidates from this line's cells but not from exept
        if exept is None:
            for cell in self.unsolved:
                cell.remove_candidates(digits)
        else:
            for cell in self.unsolved:
                if cell not in exept:
                    cell.remove_candidates(digits)
    
    def update(self):
        for pos in self._to_elliminate:
            self._unsolved.pop(pos)
        self._to_elliminate = set()
    
    def is_solved(self):
        return len(self._unsolved) == 0
    
    def __getitem__(self, key):
        return self.cells[key]
    
    def __len__(self):
        return len(self.cells)

    def __repr__(self):
        length = len(self.cells)
        matrix = np.zeros((3, 3*length), dtype = int)
        string = '\n'
        for k, cell in enumerate(self.cells):
            matrix[:, 3*k:3*k+3] = cell.matrix_repr()
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if matrix[i][j] == 0:
                    string += ' '
                else:
                    string += str(matrix[i][j])
                if (j + 1) % 3 == 0:
                    string += ' '
            string += '\n'
        return string
        
class Compartment(CellGroup):
    def __init__(self, cells, hook = None):
        super().__init__(cells, hook)
        # some more parameters
        self.missing_digits = [] # digits needed to complete the gaps between the required digits
        self.sure_digits = [] # digits that must be in the straigth but are not yet pinned down. includes missing_digits
        self.propagate_missing = False # wheter we already removed the digits from the rest of the line
        self.propagate_sure = False # if true, implies propagate_missing since sure_digits includes missing_digits (as a set)
        self.update()

    def update(self): # returns true if the str8 is completely solved
        super().update() # this takes care of the unsolved list
        if len(self.unsolved) == 0: # see if we have something to solve
            # do a sanity check
            strait = [ cell.candidates for cell in self.cells ] # check that this is actually a strait
            strait.sort()
            last = strait[0]
            for i in strait:
                if i - last > 1:
                    raise NoSolutionPossible('Compartment was completed but not with a strait')
                last = i
            return True
        # all the candidate digits from all the cells in the straigth
        self.possible = non_void_union( [ C.candidates for C in self.unsolved ] ) # this is a multiset
        if len(self.possible) == 0:
            raise NoSolutionPossible("Compartment has no possible range.")
        # the digits that are already pinned down
        self.required = [ C.candidates for C in self.cells if C.is_solved() ]
        self.required.sort()
        return False
    
    @property
    def horizontal(self):
        return self.cells[0][0] == self.cells[1][0] # we have at least 2 cells so this is ok

    def get_containing_group(self, board):
        if self.horizontal:
            return board.lines[self.cells[0][0]]
        else:
            return board.cols[self.cells[0][1]]

def get_compartment_limits(vector):
    ''' Splits a 1d vector into straits '''
    blocked = True
    start_idx = 0
    str8ts = []
    for idx, el in enumerate(vector):
        if blocked and el == 0:# new beghinning
            start_idx = idx
            blocked = False
        if not blocked and el == 1:# new end
            end_idx = idx - 1
            blocked = True
            if start_idx < end_idx: # compartments of length one are useless for analysis
                str8ts.append((start_idx, end_idx))
    if not blocked:
        end_idx = len(vector) - 1
        if start_idx < end_idx:
            str8ts.append((start_idx, len(vector)-1))
    return str8ts

def get_compartment_indices(block_matrix):
    comp = []
    for i in range(len(block_matrix)):
        line = get_compartment_limits(block_matrix[i, :])
        line_comp = [ [(i, j) for j in range(com[0], com[1]+1)] for com in line ]
        col = get_compartment_limits(block_matrix[:, i])
        col_comp = [ [(j, i) for j in range(com[0], com[1]+1)] for com in col ]
        comp.extend(line_comp)
        comp.extend(col_comp)
    return comp

class BoardLine(CellGroup):
    # This class represents a line or column of the board.
    # The cells field contains _ALL_ the cells in the line, including
    # the blocked ones and the solved ones. For the uncompleted cells
    # there is the unsolved field from the base class.
    def __init__(self, cells, hook = None):
        super().__init__(cells, hook) # vert is True if this is a column
        self._to_propagate = set() # values that we need to propagate.
        self._updating = False
    
    def _cell_changed(self, cell): # this has to be completely rewritten because of the hook
        self.changed = True # the changed flag is used by the naked pairs/triples strategies
        if cell.is_solved(): # propagate changes through the line
            cell = self._unsolved[cell.pos]
            self._to_propagate.add(cell.candidates) # candidates should be a number
            self._to_elliminate.add(cell.pos)
            if not self._updating:
                self.hook(line = self)
            
    def update(self):
        self._updating = True
        # _to_elliminate is not void if and only if _to_propagate is not void
        while len(self._to_elliminate) != 0:
            if len(self._to_propagate) != len(self._to_elliminate):
                raise NoSolutionPossible('Two or more cells propagated the same digit')
            super().update() # this takes care of the _to_elliminate field

            # and then remove the candidates in values from all the cells in self._unsolved
            candidates = self._to_propagate # i have to do this because if a cell is solved, it will
            self._to_propagate = set() # call cell_changed and it will append another value to self._to_propagate
            for cell in self.unsolved: # cell_changed() doesn't touch _unsolved so we can iterate through it
                cell.remove_candidates(candidates)

        self._updating = False

class Board:
    def __init__(self, config = None, cells = None, blocked = None):
        '''
        config must be an np.array with dimensions 2 x 9 x 9.
        The subarray 0 x size x size contains 0 if the cell must be completed or 1 if it's blocked.
        The subarray 1 x size x size contains the clues.
        '''
        # make the set of lines/columns to be updated
        self._to_update = set()
        # the set of compartments that need to be rechecked because they changed
        self._com_changed = set()
        if cells is not None:
            if blocked is None:
                raise ValueError("Can't initialize from cells if blocked is not given")
            self.blocked = blocked # it's not necessary to copy this since we're not modifying it anywere
            self._cells = tuple( cell.copy() for cell in cells ) # copy all the cells over
            board_size = self.blocked.shape[0] # blocked is a np.array object
            self._init_lines_and_columns(board_size)
            # there's no need to update anything so we're good
        elif config is not None:
            self._init_from_config(config)
        else:
            raise ValueError("config and cells cannot both be None")
        # and now calculate the compartments
        self._init_compartments()

    def _init_lines_and_columns(self, board_size):
        hook = Hook(self._line_changed) # prepare the hook for the lines and columns
        self.lines = tuple(BoardLine(self._cells[i*board_size:(i+1)*board_size], hook = hook) for i in range(board_size))
        self.cols = tuple( BoardLine([line[j] for line in self.lines], hook = hook) for j in range(board_size) )
        
    def _init_from_config(self, config):
        shape = config.shape
        if len(shape) != 3 or shape[1] != shape[2] or shape[0] != 2 or shape[1] != 9:
            raise ValueError("config must have shape 2 x 9 x 9.")
        board_size = shape[1]
        self.blocked = config[0] # remember what cells are blocked or not for printing purposes and for calculating compartments

        # create all the necessary cells (board_size * board_size in total)
        self._cells = tuple( Cell(size = board_size, pos = (i // board_size, i % board_size)) for i in range(board_size*board_size) )
        # and now put them in lines and columns
        self._init_lines_and_columns(board_size)
        # and now fix the clues and blocked cells
        for i in range(board_size):
            for j in range(board_size):
                if config[0][i][j] == 1:
                    if config[1][i][j] != 0:
                        self.lines[i][j].candidates = int(config[1][i][j])
                    else:
                        cell = self.lines[i][j]
                        cell._possible = {0} # avoid triggering all the hooks
                        self.lines[i]._unsolved.pop(cell.pos) # and remove this from the unsolved list
                        self.cols[j]._unsolved.pop(cell.pos) # of it's line and column
                elif config[1][i][j] != 0:
                    self.lines[i][j].candidates = int(config[1][i][j])
        # and update stuff
        self.update()

    def _init_compartments(self):
        indices = get_compartment_indices(self.blocked)
        hook = Hook(self._compartment_changed)
        compartments =  [ Compartment([self.get_cell_at(pos) for pos in idx], hook = hook) for idx in indices ]
        compartments.sort(key = lambda com : len(com))
        self._compartments = compartments

    def _line_changed(self, line): # hook
        self._to_update.add(line)

    def _compartment_changed(self, compartment): # hook
        self._com_changed.add(compartment)

    def update(self):
        updating = self._to_update
        self._to_update = set()
        while len(updating) != 0:
            for line in updating:
                line.update()
            updating = self._to_update
            self._to_update = set()

    def is_solved(self):
        for line in self.lines:
            if not line.is_solved():
                return False
        return True

    def get_cell_at(self, idx):
        return self.lines[idx[0]][idx[1]]

    def copy(self):
        return Board(cells = self._cells, blocked = self.blocked)

    def __getitem__(self, key):
        return self.lines[key]

    @property
    def size(self):
        return len(self.lines)

    def __repr__(self):
        string = ''
        matrix = np.zeros((27,27),dtype = object)
        board_size = len(self.lines)
        if board_size != 9:
            return 'Board too big'
        for i in range(board_size):
            for j in range(board_size):
                cell = self.lines[i][j].matrix_repr()
                if self.blocked[i][j] == 1:
                    cell[0] = 'X'
                    cell[2] = 'X'
                    cell[1][0] = 'X'
                    cell[1][2] = 'X'
                    if cell[1][1] == 0:
                        cell[1][1] = 'X'
                matrix[3*i:3*i+3, 3*j:3*j+3] = cell
        for i in range(27):
            for j in range(27):
                if matrix[i][j] == 0:
                    string += ' '
                else:
                    string += str(matrix[i][j])
                if (j + 1) % 3 == 0:
                    string += ' '
            string += '\n'
            if (i + 1) % 3 == 0:
                string += '\n'
        return string

def apply_strategy(board, strategy):
    changed = board._com_changed
    board._com_changed = set()
    while len(changed) != 0:
        for compartment in changed:
            if strategy(compartment):
                board.update()
                propagate_changes(board, compartment)
                success = True
            apply_compartment_strategies(board, compartment)
        changed = board._com_changed
        board._com_changed = set()
    
def apply_compartment_strategies(board, compartment):
    if compartment.update():
        # we don't need to return anything because the hooks mechanism takes care of
        # putting the compartment in the _com_changed() set
        return 
    for func in STRATEGIES:
        if func(compartment):
            board.update()
            propagate_changes(board, compartment)
            return # stop at the first successfull strategy so that the compartment can be updated again

def use_strategies(board):
    board.update()
    changed = board._com_changed
    board._com_changed = set()
    while len(changed) != 0:
        for compartment in changed:
            apply_compartment_strategies(board, compartment)
        changed = board._com_changed
        board._com_changed = set()

def start_strategies(board):
    board._com_changed = set(board._compartments)
    use_strategies(board)
# the strategies:

def compartment_check(strait):
    if len(strait.required) != 0: # this means we have some anchors, and maybe we can do something
        # figure out if there are gaps between our anchors
        missing = get_missing(strait.required)
        # now these missing numbers, if any, must be present in the strait, and therefore
        # cannot be present anywhere else on the same line/collumn
        if missing != strait.missing_digits:
            # save this to propagate the changes
            strait.propagate_missing = True
            strait.missing_digits = missing
        success=  max_range(strait)
    else:
        unsolved_min, unsolved_max = get_unsolved_max_range(strait)
        success =  update_max_range(strait, unsolved_min, unsolved_max)
    return success

def isolated_digits(strait):
    # for each unsolved cell see if there exist digits whose
    # neighbour digits are not present in the rest of the compartment
    # These can be elliminated because clearly they can't form a strait
    cache = strait.possible.copy()
    cache.update(strait.required)
    success = False
    for cell in strait.unsolved:
        available = cache.copy() # copy the possible multiset so we don't destroy it
        available.subtract(cell.candidates) # this is to remove candidates that are only in this cell
        available = { key for key, val in available.items() if val != 0 }
        remove = []
        for d in cell: #.candidates:
            if ((d-1) not in available and (d+1) not in available):
                remove.append(d)
                success = True
        cell.remove_candidates(remove)
    return success

def sure_digits(strait):
    min_digit, max_digit = get_unsolved_max_range(strait) # check the actual range, maybe we can improve it
    if len(strait.required) != 0:
        min_digit = min(min_digit, strait.required[0])
        max_digit = max(max_digit, strait.required[-1])
    lowest_range = (min_digit, min_digit + len(strait) - 1)
    highest_range = (max_digit - len(strait) + 1, max_digit)
    # and now get the intersection of the two ranges
    sure = [ i for i in range(highest_range[0], lowest_range[1] + 1) ]
    if sure != strait.sure_digits:
        strait.sure_digits = sure
        if len(sure) > len(strait.required):
            strait.propagate_sure = True
            return True
    return False

def check_unique(strait):
    success = False
    if len(strait.sure_digits) == len(strait):
        # see if there exists a possible digit with only one occurence
        for d in strait.sure_digits:
            nr = strait.possible[d] # how many cells contain this number
            if nr == 1:
                # because this digit appears in only one cell and because it is a sure digit,
                # we just solved the cell which contains this candidate
                for cell in strait.unsolved:
                    if d in cell: #.candidates:
                        cell.candidates = d
                        success = True
    return success

def stranded_digits(strait):
    # check for digits that cannot complete this strait because there
    # isn't enough of them
    available = list(strait.possible)
    available.extend(strait.required)
    available.sort()
    start_seq = available[0]
    end_seq = available[0]
    stranded = []
    for d in available:
        if d - end_seq > 1:
            if end_seq - start_seq + 1 < len(strait):
                stranded.extend([ i for i in range(start_seq, end_seq+1) ])
            start_seq = d
        end_seq = d
    if available[-1] - start_seq + 1 < len(strait):
        stranded.extend( [ i for i in range(start_seq, available[-1]+1) ] )
    if len(stranded) != 0:
        strait.propagate(stranded)
        return True
    return False

# These are all the strategies implemented so far
STRATEGIES = [compartment_check, isolated_digits, sure_digits, check_unique, stranded_digits ]

# And some more utility functions 
def get_missing(sorted_vector):
    # get a list of all the numbers missing from the sorted_vector of integers
    gaps = []
    last = sorted_vector[0]
    for i in sorted_vector:
        for j in range(last+1, i):
            gaps.append(j)
        last = i
    return gaps

def get_solved_max_range(strait):
    req_min = strait.required[0]
    req_max = strait.required[-1]
    seq_range = len(strait.unsolved) - len(strait.missing_digits)
    solved_min = req_min - seq_range
    solved_max = req_max + seq_range
    return solved_min, solved_max
    
def get_unsolved_max_range(strait):
    min_reached = min(strait.possible)
    max_reached = max(strait.possible)
    for cell in strait.unsolved:
        min_reached = max(min_reached, min(cell.candidates) - len(strait) + 1)
        max_reached = min(max_reached, max(cell.candidates) + len(strait) - 1)
    return min_reached, max_reached
    
def update_max_range(strait, new_min, new_max):
    old_min = min(strait.possible)
    old_max = max(strait.possible)
    if new_min > old_min or new_max < old_max:
        strait.propagate({i for i in range(old_min, new_min)})
        strait.propagate({i for i in range(new_max+1, old_max+1)})
        return True
    return False

def max_range(strait):
    # figure out the max range possible
    # strait.required should be sorted
    solved_min, solved_max = get_solved_max_range(strait)
    unsolved_min, unsolved_max = get_unsolved_max_range(strait)
    new_min = max(solved_min, unsolved_min)
    new_max = min(solved_max, unsolved_max)
    return update_max_range(strait, new_min, new_max)

def propagate_changes(board, strait):
    digits = []
    if strait.propagate_sure:
        strait.propagate_sure = False
        strait.propagate_missing = False
        digits = strait.sure_digits
    elif strait.propagate_missing:
        strait.propagate_missing = False
        digits = strait.missing_digits
    else:
        return
    group = strait.get_containing_group(board)
    group.propagate(digits, strait.unsolved)
    board.update()
    strait.propagate_missing = False

# The Graph search algorithm

def find_best_cell_idx(board):
    min_len = board.size # the maximum nr of possibilities is equal to the board size
    min_idx = -1
    for i, cell in enumerate(board._cells):
        if len(cell) > 1 and len(cell) < min_len:
            min_len = len(cell)
            min_idx = i
    return min_idx

def depth_first_search(board):
    try:
        start_strategies(board)
        #use_strategies(board) # this updates the board inplace
        if board.is_solved():
            return board
    except NoSolutionPossible:
        return None
    # the states in the stack are tuples of the form
    # if we got here, it means the solver got stuck.
    idx = find_best_cell_idx(board)
    candidates = board._cells[idx]._possible.copy()
    for c in candidates:
        board_copy = board.copy()
        board_copy._cells[idx].candidates = c
        #board_copy.update()
        result = depth_first_search(board_copy)
        if result is not None:
            return result # we're done here, all good

# And this is the function that solves a board.
# The file should contain an np.array of dimensions
# 2 x 9 x 9. The first 9 x 9 subarray should have
# 1 where there are blocked cells, and 0 elsewhere,
# and the second array should have the clues on their
# positions and 0 in the rest.
def solve_game(file):
    config = np.load(file)
    B = Board(config)
    B = depth_first_search(B)
    return B