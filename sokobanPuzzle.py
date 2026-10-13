from copy import deepcopy
class SokobanPuzzle:
    def __init__(self,board):
        self.height = len(board)
        self.width = len(board[0])
        self.board = deepcopy(board)

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

    def succesorsFunction(self):      
        successors =[]
        etat_actuel = self.board
        r,c = self.robot_position
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
            if target_cell == '0':
              continue
            if target_cell == '':
              new_board = deepcopy(etat_actuel)
              new_board[target_r][target_c] ='R' 
              new_board[r][c] = ''
              new_puzzle = SokobanPuzzle(new_board)
              successors.append((new_puzzle, move))    
            if target_cell == 'B':
              box_target_r, box_target_c = target_r + (target_r - r), target_c + (target_c - c)
              if not (0 <= box_target_r < self.height and 0 <= box_target_c < self.width):
               continue
              box_target_cell = etat_actuel[box_target_r][box_target_c]
              if box_target_cell == '0' or box_target_cell == 'B':
               continue
              new_board = deepcopy(etat_actuel)
              new_board[target_r][target_c] = 'R'
              new_board[r][c] = ''
              new_board[box_target_r][box_target_c] = 'B'
              new_puzzle = SokobanPuzzle(new_board)
              successors.append((new_puzzle, move))
        return successors