import time

from main import NIVEAUX
from sokobanPuzzle import SokobanPuzzle
from search import BFS, AStar
from heuristique import heuristique_1, heuristique_2, heuristique_3

# (nom affiché, fonction qui prend un état et renvoie (noeud, expanded))
METHODES = [
    ("BFS",     lambda etat: BFS(etat)),
    ("A* + h1", lambda etat: AStar(etat, heuristique_1)),
    ("A* + h2", lambda etat: AStar(etat, heuristique_2)),
    ("A* + h3", lambda etat: AStar(etat, heuristique_3)),
]


def creer_etat(grille):
    """Transforme une liste de chaînes en SokobanPuzzle."""
    largeur = max(len(ligne) for ligne in grille)
    return SokobanPuzzle([list(ligne.ljust(largeur, 'O')) for ligne in grille])


def solution_valide(initial, solution):
    """Rejoue les actions depuis l'état initial et vérifie qu'on arrive au but."""
    etat = initial
    for action in solution.getSolution():
        suivant = None
        for a, s in etat.successorFunction():
            if a == action:
                suivant = s
                break
        if suivant is None:          # action impossible : solution invalide
            return False
        etat = suivant
    return etat.isGoal()


def main():
    print(f"{'Niveau':<15}{'Méthode':<10}{'Coût':>6}{'Nœuds':>9}{'Temps (s)':>11}  Remarque")
    print("-" * 70)

    for nom, grille in NIVEAUX:
        initial = creer_etat(grille)
        cout_bfs = None                       # coût optimal, donné par BFS

        for nom_methode, methode in METHODES:
            debut = time.perf_counter()
            solution, noeuds = methode(initial)
            temps = time.perf_counter() - debut

            if solution is None:
                print(f"{nom:<15}{nom_methode:<10}{'-':>6}{noeuds:>9}{temps:>11.3f}  pas de solution")
                continue

            cout = solution.g
            remarque = ""
            if not solution_valide(initial, solution):
                remarque = "SOLUTION INVALIDE !"
            elif nom_methode == "BFS":
                cout_bfs = cout
            elif cout_bfs is not None and cout > cout_bfs:
                remarque = f"non optimal (+{cout - cout_bfs})"

            print(f"{nom:<15}{nom_methode:<10}{cout:>6}{noeuds:>9}{temps:>11.3f}  {remarque}")
        print()


if __name__ == "__main__":
    main()