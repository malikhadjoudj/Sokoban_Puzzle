def heuristique_1(state):
    #nombre de caisse pas encore mise dans les cases cible
    h1=0
    for i in range(state.height):
                for j in range(state.width):
                        if state.board[i][j] == 'B':
                            h1=h1+1

    return h1

def heuristique_2(state):
       #distance entre une caisse et une cible
       h2=0
       for i in range(state.height):
                       for j in range(state.width):
                               if state.board[i][j] == 'B':
                                  min_distance = float('inf')
                                  for a in range(state.height):
                                        for b in range(state.width):
                                                if state.board[a][b]=='S'or state.board[a][b]=='.':
                                                        
                                                        d= abs(i-a)+abs(j-b)
                                                        if d<min_distance:
                                                            min_distance=d
                                  h2 = h2 + min_distance
       return  2*heuristique_1(state) + h2


def heuristique_3(state):
    # h3 = h2 + distance de Manhattan entre le robot et la caisse la plus proche
    robot = state.robot_position          # (ligne, colonne) du robot
    min_distance = float('inf')
    for i in range(state.height):
        for j in range(state.width):
            if state.board[i][j] == 'B':
                d = abs(robot[0] - i) + abs(robot[1] - j)
                if d < min_distance:
                    min_distance = d
    if min_distance == float('inf'):      # plus aucune caisse B : on n'ajoute rien
        min_distance = 0
    return heuristique_2(state) + min_distance
