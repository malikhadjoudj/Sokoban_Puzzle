from sokobanPuzzle import SokobanPuzzle
from search import BFS

# Légende : O = mur, ' ' = vide, S = cible, B = caisse, R = joueur
# . = joueur sur cible, * = caisse sur cible
EXEMPLE_3 = [
    "OOOOOOOO",
    "O      O",
    "O  BR  O",
    "O   OB O",
    "OOOOOSOO",
    "OOOOOSOO",
    "OOOOOOOO",
]

def afficher(etat):
    for ligne in etat.board:
        print("".join(ligne))
    print()

if __name__ == "__main__":
    # chaque ligne devient une liste de caractères (liste de listes)
    board = [list(ligne) for ligne in EXEMPLE_3]
    initial = SokobanPuzzle(board)

    print("Etat initial :")
    afficher(initial)

    solution = BFS(initial)

    if solution is None:
        print("Pas de solution")
    else:
        print("Solution :", solution.getSolution())
        print("Cout (g) :", solution.g)
        print("Nombre de coups :", len(solution.getSolution()))
        print()

        # simulation : on affiche chaque état du chemin
        for i, etat in enumerate(solution.getPath()):
            print(f"Etape {i} :")
            afficher(etat)