from copy import deepcopy
class SokobanPuzzle:
    def __init__(self,board):
        self.height = len(board)
        self.width = len(board[0])
        self.board = deepcopy(board)
        robot_position = None
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] == 'R':
                    robot_position = (i,j)
                if self.board[i][j] == '.':
                    robot_position = (i,j)

        self.robot_position = robot_position
        self.moves = ['U', 'D', 'L', 'R']

    def isGoal(self):
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] == 'B':
                    return False
        return True   
    def __eq__(self, other):
        return isinstance(other, SokobanPuzzle) and self.board == other.board

    def __hash__(self):
        return hash(tuple(tuple(ligne) for ligne in self.board))
    
    def successorFunction(self):      
        successors =[]
        etat_actuel = self.board
        r,c = self.robot_position
        # ce que devient la case quittée par le robot
        case_quittee = 'S' if etat_actuel[r][c] == '.' else ' '
        for move in self.moves:
            if move == 'U':
                target_r, target_c = r-1, c
            elif move == 'D':
                target_r, target_c = r+1, c
            elif move == 'L':
                target_r, target_c = r, c-1
            elif move == 'R':
                target_r, target_c = r, c+1

            if not (0 <= target_r < self.height and 0 <= target_c < self.width):
              continue
            target_cell = etat_actuel[target_r][target_c]
            if target_cell == 'O':
              continue
            if target_cell == ' ' or target_cell == 'S':
              new_board = deepcopy(etat_actuel)
              new_board[target_r][target_c] = '.' if target_cell == 'S' else 'R'
              new_board[r][c] = case_quittee
              new_puzzle = SokobanPuzzle(new_board)
              successors.append((move, new_puzzle))    
            elif target_cell == 'B'or target_cell == '*':
              box_target_r, box_target_c = target_r + (target_r - r), target_c + (target_c - c)
              if not (0 <= box_target_r < self.height and 0 <= box_target_c < self.width):
               continue
              box_target_cell = etat_actuel[box_target_r][box_target_c]
              if box_target_cell not in (' ', 'S'):   # mur, caisse ou caisse sur cible
                continue
              new_board = deepcopy(etat_actuel)
              new_board[target_r][target_c] = '.' if target_cell == '*' else 'R'
              new_board[r][c] = case_quittee
              new_board[box_target_r][box_target_c] = '*' if box_target_cell == 'S' else 'B'
              new_puzzle = SokobanPuzzle(new_board)
              successors.append((move, new_puzzle))
        return successors