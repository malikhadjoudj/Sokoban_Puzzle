from copy import deepcopy
WALL = 'O'
EMPTY = ' '
TARGET = 'S'
BOX = 'B'
PLAYER = 'R'
PLAYER_ON_TARGET = '.'
BOX_ON_TARGET = '*'

LEAVE       = {PLAYER: EMPTY, PLAYER_ON_TARGET: TARGET}
ARRIVE      = {EMPTY: PLAYER, TARGET: PLAYER_ON_TARGET}
PUSH_ARRIVE = {BOX: PLAYER, BOX_ON_TARGET: PLAYER_ON_TARGET}
BOX_ARRIVE  = {EMPTY: BOX, TARGET: BOX_ON_TARGET}


class SokobanPuzzle:
    def __init__(self, board):
        self.board = deepcopy(board)
        self.height = len(self.board)
        self.width = len(self.board[0])
        self.robot_position = None
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] in (PLAYER, PLAYER_ON_TARGET):
                    self.robot_position = (i, j)
        self.moves = {'UP': (-1, 0), 'DOWN': (1, 0), 'LEFT': (0, -1), 'RIGHT': (0, 1)}

    def isGoal(self):
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] == BOX:
                    return False
        return True

    def successorFunction(self):
        successors = []
        etat_actuel = self.board
        r, c = self.robot_position
        for move, (dr, dc) in self.moves.items():
            target_r, target_c = r + dr, c + dc
            if not (0 <= target_r < self.height and 0 <= target_c < self.width):
                continue
            target_cell = etat_actuel[target_r][target_c]

            if target_cell == WALL:
                continue

            if target_cell in (EMPTY, TARGET):
                new_board = deepcopy(etat_actuel)
                new_board[r][c] = LEAVE[etat_actuel[r][c]]
                new_board[target_r][target_c] = ARRIVE[target_cell]
                successors.append((move, SokobanPuzzle(new_board)))

            elif target_cell in (BOX, BOX_ON_TARGET):
                box_r, box_c = target_r + dr, target_c + dc
                if not (0 <= box_r < self.height and 0 <= box_c < self.width):
                    continue
                box_cell = etat_actuel[box_r][box_c]
                if box_cell not in (EMPTY, TARGET):
                    continue
                new_board = [row[:] for row in etat_actuel]
                new_board[r][c] = LEAVE[etat_actuel[r][c]]
                new_board[target_r][target_c] = PUSH_ARRIVE[target_cell]
                new_board[box_r][box_c] = BOX_ARRIVE[box_cell]
                successors.append((move, SokobanPuzzle(new_board)))
        return successors

    def __eq__(self, other):
        return self.board == other.board

    def __hash__(self):
        return hash(tuple(tuple(row) for row in self.board))



    