from sokobanPuzzle import SokobanPuzzle
from search import BFS

# Niveaux : O = mur, ' ' = vide, S = cible, B = caisse, R = joueur,
# . = joueur sur cible, * = caisse sur cible.
# Pour ajouter un niveau : ajouter un tuple (nom, grille) dans NIVEAUX.
EXEMPLE_1 = [
    "OOOOOO",
    "OS B O",
    "O OR O",
    "O    O",
    "O    O",
    "OOOOOO",
]

EXEMPLE_2 = [
    "OOOOOOOOO",
    "O       O",
    "O       O",
    "O  OOO  O",
    "O    O. O",
    "O     O O",
    "O  B  O O",
    "O     O O",
    "OOOOOOOOO",
]

EXEMPLE_3 = [
    "OOOOOOOO",
    "O      O",
    "O  BR  O",
    "O   OB O",
    "OOOOOSOO",
    "OOOOOSOO",
    "OOOOOOOO",
]

EXEMPLE_4 = [
    "OOOOOOO",
    "OO  OOO",
    "OO  OOO",
    "OO *  O",
    "OOBOB O",
    "O SRS O",
    "O    OO",
    "OOO  OO",
    "OOOOOOO",
]

EXEMPLE_5 = [
    "OOOOOOOOO",
    "OOOSO  OO",
    "O    B OO",
    "O B R  SO",
    "OOO O OOO",
    "OOOBO OOO",
    "OOO  SOOO",
    "OOOOOOOOO",
]

EXEMPLE_IMPOSSIBLE = [      # la caisse est coincée dans un coin : pas de solution
    "OOOOOO",
    "OBR SO",
    "O    O",
    "OOOOOO",
]

NIVEAUX = [
    ("Exemple 1", EXEMPLE_1),
    ("Exemple 2", EXEMPLE_2),
    ("Exemple 3", EXEMPLE_3),
    ("Exemple 4", EXEMPLE_4),
    ("Exemple 5", EXEMPLE_5),
    ("Sans solution", EXEMPLE_IMPOSSIBLE),
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

    solution, expanded = BFS(initial)

    if solution is None:
        print("Pas de solution")
    else:
        print("Solution :", solution.getSolution())
        print("Cout (g) :", solution.g)
        print("Nombre de coups :", len(solution.getSolution()))
        print("Noeuds explores :", expanded)
        print()

        # simulation : on affiche chaque état du chemin
        for i, etat in enumerate(solution.getPath()):
            print(f"Etape {i} :")
            afficher(etat)