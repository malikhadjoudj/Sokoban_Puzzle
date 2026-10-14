from sokobanPuzzle import SokobanPuzzle
from search import BFS

level = [['O','O','O','O','O'],
         ['O','S',' ',' ','O'],
         ['O',' ','B',' ','O'],
         ['O',' ','R',' ','O'],
         ['O','O','O','O','O']]
print("Début du test")
p = SokobanPuzzle(level)
print("Robot en :", p.robot_position)
print("Nombre de successeurs :", len(p.successorFunction()))



goal = BFS(SokobanPuzzle(level))

if goal is None:
    print("Pas de solution")
else:
    print("Solution :", goal.getSolution())
    print("Coût :", goal.g)