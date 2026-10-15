"""Interface Pygame pour visualiser la résolution du Sokoban par BFS.

Lancer avec :  python gui.py
"""
import pygame

from sokobanPuzzle import SokobanPuzzle
from search import BFS

# ----------------------------------------------------------------------
# Niveaux : O = mur, ' ' = vide, S = cible, B = caisse, R = joueur,
# . = joueur sur cible, * = caisse sur cible.
# Pour ajouter un niveau : ajouter un tuple (nom, grille) dans NIVEAUX.
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# Paramètres d'affichage
# ----------------------------------------------------------------------
TAILLE_MAX_CASE = 80
LARGEUR_MAX_GRILLE = 900
HAUTEUR_MAX_GRILLE = 650
LARGEUR_PANNEAU = 330
HAUTEUR_MIN_FENETRE = 420
DELAI_DEFAUT = 400      # ms entre deux étapes
DELAI_MIN = 50
DELAI_MAX = 2000
PAS_DELAI = 50

# Couleurs (R, G, B)
C_FOND = (255, 255, 255)
C_MUR = (140, 140, 140)
C_MUR_JOINT = (70, 70, 70)
C_SOL = (253, 222, 190)
C_SOL_LIGNE = (255, 238, 215)
C_CIBLE = (60, 60, 60)
C_CAISSE = (120, 60, 25)
C_CAISSE_FENTE = (60, 28, 10)
C_CAISSE_CIBLE = (235, 235, 40)
C_CAISSE_CIBLE_FENTE = (110, 120, 20)
C_PEAU = (245, 200, 160)
C_CHEVEUX = (40, 30, 25)
C_CHEMISE = (210, 210, 205)
C_PANTALON = (40, 100, 200)
C_TEXTE = (30, 30, 30)
C_TEXTE_GRIS = (100, 100, 100)
C_ERREUR = (200, 30, 30)


# ----------------------------------------------------------------------
# Préparation des données
# ----------------------------------------------------------------------
def creer_etat_initial(niveau):
    """Transforme une liste de chaînes en SokobanPuzzle (liste de listes)."""
    largeur = max(len(ligne) for ligne in niveau)
    # on complète les lignes trop courtes avec des murs
    board = [list(ligne.ljust(largeur, 'O')) for ligne in niveau]
    return SokobanPuzzle(board)


def calculer_taille_case(hauteur, largeur):
    """Choisit la taille d'une case pour que la grille tienne à l'écran."""
    return max(10, min(TAILLE_MAX_CASE,
                       LARGEUR_MAX_GRILLE // largeur,
                       HAUTEUR_MAX_GRILLE // hauteur))


def creer_fenetre(etat):
    """Crée la fenêtre, dimensionnée selon la grille. Retourne (écran, taille_case)."""
    taille = calculer_taille_case(etat.height, etat.width)
    larg = etat.width * taille + LARGEUR_PANNEAU
    haut = max(etat.height * taille, HAUTEUR_MIN_FENETRE)
    return pygame.display.set_mode((larg, haut)), taille


def lancer_recherche(ecran, police, etat):
    """Affiche 'Recherche en cours...' puis lance BFS.
    Retourne (chemin, solution, nb_noeuds)."""
    ecran.fill(C_FOND)
    texte = police.render("Recherche en cours...", True, C_TEXTE)
    ecran.blit(texte, texte.get_rect(center=ecran.get_rect().center))
    pygame.display.flip()
    pygame.event.pump()     # évite que la fenêtre soit marquée "ne répond pas"

    solution, nb_noeuds = BFS(etat)
    chemin = solution.getPath() if solution is not None else [etat]
    return chemin, solution, nb_noeuds


# ----------------------------------------------------------------------
# Dessin (style briques / caisses en bois / petit personnage)
# ----------------------------------------------------------------------
def dessiner_mur(ecran, rect):
    """Mur en briques : fond gris + joints sombres décalés une ligne sur deux."""
    pygame.draw.rect(ecran, C_MUR, rect)
    haut_brique = rect.h // 3
    for k in range(3):
        y = rect.y + k * haut_brique
        pygame.draw.line(ecran, C_MUR_JOINT, (rect.x, y), (rect.right, y), 1)
        decalage = rect.w // 2 if k % 2 else rect.w // 4
        pygame.draw.line(ecran, C_MUR_JOINT, (rect.x + decalage, y),
                         (rect.x + decalage, y + haut_brique), 1)
    pygame.draw.rect(ecran, C_MUR_JOINT, rect, 1)


def dessiner_sol(ecran, rect):
    """Sol beige/pêche avec un fin quadrillage."""
    pygame.draw.rect(ecran, C_SOL, rect)
    pygame.draw.rect(ecran, C_SOL_LIGNE, rect, 1)


def dessiner_cible(ecran, rect):
    """Carré en pointillés avec une petite croix au centre."""
    marge = max(2, rect.w // 10)
    r = rect.inflate(-2 * marge, -2 * marge)
    pas = max(4, rect.w // 8)
    for t in range(0, r.w, pas * 2):                         # côtés horizontaux
        x2 = min(r.x + t + pas, r.right)
        pygame.draw.line(ecran, C_CIBLE, (r.x + t, r.y), (x2, r.y), 2)
        pygame.draw.line(ecran, C_CIBLE, (r.x + t, r.bottom), (x2, r.bottom), 2)
    for t in range(0, r.h, pas * 2):                         # côtés verticaux
        y2 = min(r.y + t + pas, r.bottom)
        pygame.draw.line(ecran, C_CIBLE, (r.x, r.y + t), (r.x, y2), 2)
        pygame.draw.line(ecran, C_CIBLE, (r.right, r.y + t), (r.right, y2), 2)
    cx, cy = r.center
    d = max(2, rect.w // 12)
    pygame.draw.line(ecran, C_CIBLE, (cx - d, cy - d), (cx + d, cy + d), 1)
    pygame.draw.line(ecran, C_CIBLE, (cx + d, cy - d), (cx - d, cy + d), 1)


def dessiner_caisse(ecran, rect, sur_cible):
    """Caisse en bois marron avec des planches (jaune si sur une cible)."""
    couleur = C_CAISSE_CIBLE if sur_cible else C_CAISSE
    fente = C_CAISSE_CIBLE_FENTE if sur_cible else C_CAISSE_FENTE
    caisse = rect.inflate(-rect.w // 8, -rect.h // 8)
    pygame.draw.rect(ecran, couleur, caisse)
    for k in range(1, 5):                                    # planches horizontales
        y = caisse.y + k * caisse.h // 5
        pygame.draw.line(ecran, fente, (caisse.x, y), (caisse.right, y), 1)
    pygame.draw.rect(ecran, fente, caisse, 2)


def dessiner_joueur(ecran, rect):
    """Petit personnage : tête, cheveux, chemise, pantalon bleu."""
    cx = rect.centerx
    u = rect.w / 10                                          # unité de dessin
    pygame.draw.rect(ecran, C_PANTALON, (cx - 2 * u, rect.y + 6.2 * u, 4 * u, 2.6 * u))
    pygame.draw.rect(ecran, C_CHEMISE, (cx - 2.5 * u, rect.y + 3.8 * u, 5 * u, 2.6 * u))
    pygame.draw.circle(ecran, C_PEAU, (cx, rect.y + 2.8 * u), 1.9 * u)
    pygame.draw.arc(ecran, C_CHEVEUX, (cx - 2 * u, rect.y + 0.8 * u, 4 * u, 4 * u),
                    0.1, 3.05, max(2, int(u)))
    for dx in (-0.7 * u, 0.7 * u):                           # yeux
        pygame.draw.circle(ecran, C_CHEVEUX, (cx + dx, rect.y + 2.9 * u), max(1, int(u / 3)))


def mur_visible(etat, i, j):
    """Un mur n'est dessiné que s'il touche une case non-mur (sinon : fond vide)."""
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            a, b = i + di, j + dj
            if 0 <= a < etat.height and 0 <= b < etat.width and etat.board[a][b] != 'O':
                return True
    return False


def dessiner_case(ecran, etat, i, j, rect):
    """Dessine une case selon son caractère."""
    caractere = etat.board[i][j]
    if caractere == 'O':
        if mur_visible(etat, i, j):
            dessiner_mur(ecran, rect)
        return
    dessiner_sol(ecran, rect)
    if caractere in ('S', '.'):                     # cible (visible sous le joueur)
        dessiner_cible(ecran, rect)
    if caractere in ('B', '*'):
        dessiner_caisse(ecran, rect, caractere == '*')
    if caractere in ('R', '.'):
        dessiner_joueur(ecran, rect)


def draw_board(ecran, etat, taille):
    """Dessine toute la grille de l'état donné."""
    for i in range(etat.height):
        for j in range(etat.width):
            rect = pygame.Rect(j * taille, i * taille, taille, taille)
            dessiner_case(ecran, etat, i, j, rect)


def ecrire(ecran, police, texte, x, y, couleur=C_TEXTE):
    """Écrit une ligne de texte et retourne la ordonnée de la ligne suivante."""
    surface = police.render(texte, True, couleur)
    ecran.blit(surface, (x, y))
    return y + surface.get_height() + 6


def draw_info(ecran, polices, x, infos):
    """Panneau latéral : algorithme, coût, nœuds explorés, étape, contrôles."""
    police, petite = polices
    y = 15
    y = ecrire(ecran, police, f"Niveau : {infos['nom']}", x, y)
    y = ecrire(ecran, police, f"Algorithme : {infos['algo']}", x, y)
    if infos['solution'] is None:
        y = ecrire(ecran, police, "Pas de solution", x, y, C_ERREUR)
    else:
        y = ecrire(ecran, police, f"Coût : {infos['cout']}", x, y)
        y = ecrire(ecran, police, f"Étape : {infos['etape']} / {infos['total']}", x, y)
    y = ecrire(ecran, police, f"Nœuds explorés : {infos['noeuds']}", x, y)
    y = ecrire(ecran, police, f"Délai : {infos['delai']} ms", x, y)
    y = ecrire(ecran, police, "EN PAUSE" if infos['pause'] else "Lecture", x, y,
               C_TEXTE_GRIS)
    y = ecrire(ecran, petite, f"Derniere touche : {infos['touche']}", x, y, C_TEXTE_GRIS)

    y += 10
    for ligne in ("ESPACE : pause / reprise",
                  "Fleche DROITE (ou D) : suivante",
                  "Fleche GAUCHE (ou Q) : precedente",
                  "R : recommencer",
                  "+ ou F : accelerer",
                  "- ou L : ralentir",
                  "N : niveau suivant", "ECHAP : quitter"):
        y = ecrire(ecran, petite, ligne, x, y, C_TEXTE_GRIS)


def dessiner_tout(ecran, polices, etat, taille, infos):
    """Redessine la fenêtre complète."""
    ecran.fill(C_FOND)
    draw_board(ecran, etat, taille)
    draw_info(ecran, polices, etat.width * taille + 15, infos)
    if infos['solution'] is None:
        # message bien visible au centre de la grille
        msg = polices[0].render("Pas de solution", True, C_ERREUR)
        rect = msg.get_rect(center=(etat.width * taille // 2, etat.height * taille // 2))
        ecran.blit(msg, rect)
    pygame.display.flip()


# ----------------------------------------------------------------------
# Programme principal
# ----------------------------------------------------------------------
def charger_niveau(index, polices):
    """Prépare un niveau : fenêtre + recherche BFS. Retourne un dictionnaire."""
    nom, grille = NIVEAUX[index]
    initial = creer_etat_initial(grille)
    ecran, taille = creer_fenetre(initial)
    chemin, solution, noeuds = lancer_recherche(ecran, polices[0], initial)
    return {'nom': nom, 'ecran': ecran, 'taille': taille, 'chemin': chemin,
            'solution': solution, 'noeuds': noeuds, 'algo': 'BFS',
            'cout': solution.g if solution is not None else None}


def touche_est(event, touches, caractere=None):
    """Vrai si la touche pressée est dans `touches` (ou produit ce caractère)."""
    return event.key in touches or (caractere is not None and event.unicode == caractere)


def main():
    pygame.init()
    pygame.display.set_caption("Sokoban - Résolution par BFS")
    polices = (pygame.font.SysFont("arial", 22), pygame.font.SysFont("arial", 17))
    horloge = pygame.time.Clock()

    index = 0
    niveau = charger_niveau(index, polices)
    etape = 0
    delai = DELAI_DEFAUT
    pause = False
    dernier_pas = pygame.time.get_ticks()
    derniere_touche = '-'
    en_cours = True

    while en_cours:
        total = len(niveau['chemin']) - 1       # nombre de coups
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
            elif event.type == pygame.KEYDOWN:
                derniere_touche = pygame.key.name(event.key)
                if event.key == pygame.K_ESCAPE:
                    en_cours = False
                elif event.key == pygame.K_SPACE:
                    pause = not pause
                elif touche_est(event, (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN)):
                    etape, pause = min(etape + 1, total), True   # pas à pas : on met en pause
                elif touche_est(event, (pygame.K_LEFT, pygame.K_q, pygame.K_a, pygame.K_UP)):
                    etape, pause = max(etape - 1, 0), True
                elif event.key == pygame.K_r:
                    etape, pause = 0, False
                    dernier_pas = pygame.time.get_ticks()
                elif touche_est(event, (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS,
                                        pygame.K_f), '+'):
                    delai = max(DELAI_MIN, delai - PAS_DELAI)       # plus rapide
                elif touche_est(event, (pygame.K_MINUS, pygame.K_KP_MINUS, pygame.K_l,
                                        pygame.K_6), '-'):
                    delai = min(DELAI_MAX, delai + PAS_DELAI)       # plus lent
                elif event.key == pygame.K_n:
                    index = (index + 1) % len(NIVEAUX)
                    niveau = charger_niveau(index, polices)
                    etape, pause = 0, False
                    dernier_pas = pygame.time.get_ticks()

        # avance automatique toutes les `delai` millisecondes
        maintenant = pygame.time.get_ticks()
        if not pause and etape < total and maintenant - dernier_pas >= delai:
            etape += 1
            dernier_pas = maintenant

        infos = {'nom': niveau['nom'], 'algo': niveau['algo'],
                 'solution': niveau['solution'], 'cout': niveau['cout'],
                 'noeuds': niveau['noeuds'], 'etape': etape, 'total': total,
                 'delai': delai, 'pause': pause, 'touche': derniere_touche}
        dessiner_tout(niveau['ecran'], polices, niveau['chemin'][etape],
                      niveau['taille'], infos)
        horloge.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
