"""Interface Pygame pour visualiser la résolution du Sokoban (BFS et A*).

Lancer avec :  python gui.py
"""
import math
import random
import time
import pygame

from sokobanPuzzle import SokobanPuzzle
from search import BFS,  AStar
from heuristique import heuristique_1, heuristique_2, heuristique_3

# Les niveaux (EXEMPLE_1..5, NIVEAUX) sont définis dans main.py
from main import NIVEAUX
METHODES = [
    ("BFS",     lambda etat: BFS(etat)),
    ("A* + h1", lambda etat: AStar(etat, heuristique_1)),
    ("A* + h2", lambda etat: AStar(etat, heuristique_2)),
    ("A* + h3", lambda etat: AStar(etat, heuristique_3)),
]

# ----------------------------------------------------------------------
# Paramètres d'affichage
# ----------------------------------------------------------------------
TAILLE_MAX_CASE = 80
LARGEUR_MAX_GRILLE = 900
HAUTEUR_MAX_GRILLE = 650
LARGEUR_PANNEAU = 350
HAUTEUR_MIN_FENETRE = 620
DELAI_DEFAUT = 400      # ms entre deux étapes
DELAI_MIN = 50
DELAI_MAX = 2000
PAS_DELAI = 50

# Couleurs (R, G, B) : ambiance "donjon de nuit"
C_FOND = (20, 22, 42)
C_FOND_HAUT = (12, 14, 32)
C_FOND_BAS = (52, 34, 72)
C_TEXTE = (236, 236, 245)
C_TEXTE_GRIS = (150, 154, 184)
C_ERREUR = (255, 105, 105)
C_OR = (255, 211, 105)
C_PANNEAU = (26, 28, 54)
C_PANNEAU_BORD = (78, 82, 134)
C_CARTE = (38, 41, 78)
C_PIERRE = (120, 124, 142)
C_MORTIER = (46, 48, 64)
C_BOIS_SOL = (208, 160, 108)
C_CIBLE_GLOW = (110, 230, 255)
C_CAISSE = (172, 106, 52)
C_CAISSE_BORD = (84, 46, 20)
C_CAISSE_OR = (244, 194, 72)
C_CAISSE_OR_BORD = (146, 96, 16)
C_PEAU = (250, 208, 170)
C_CHEVEUX = (62, 40, 30)
C_VESTE = (70, 128, 224)
C_BONNET = (228, 72, 72)
C_PANTALON = (52, 62, 112)
C_BOTTES = (66, 42, 30)
C_ALGOS = [(80, 150, 255), (90, 210, 130), (255, 170, 70), (200, 120, 255)]


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


def lancer_recherches(ecran, police, etat):
    """Lance toutes les méthodes l'une après l'autre.
    Retourne une liste de dictionnaires (un par méthode)."""
    resultats = []
    for nom_methode, methode in METHODES:
        dessiner_fond(ecran)
        texte = police.render(f"Recherche : {nom_methode}...", True, C_OR)
        ecran.blit(texte, texte.get_rect(center=ecran.get_rect().center))
        pygame.display.flip()
        pygame.event.pump()     # évite que la fenêtre soit marquée "ne répond pas"

        debut = time.perf_counter()
        solution, nb_noeuds = methode(etat)
        temps = time.perf_counter() - debut

        chemin = solution.getPath() if solution is not None else [etat]
        resultats.append({'algo': nom_methode, 'solution': solution,
                          'noeuds': nb_noeuds, 'temps': temps, 'chemin': chemin,
                          'cout': solution.g if solution is not None else None})
    return resultats


# ----------------------------------------------------------------------
# Outils de dessin : cache des tuiles, couleurs, ombres
# ----------------------------------------------------------------------
_CACHE = {}


def en_cache(cle, fabrique):
    """Fabrique une surface une seule fois puis la réutilise (plus fluide)."""
    if cle not in _CACHE:
        _CACHE[cle] = fabrique()
    return _CACHE[cle]


def nuance(couleur, delta):
    """Éclaircit (delta > 0) ou assombrit (delta < 0) une couleur."""
    return tuple(max(0, min(255, v + delta)) for v in couleur)


def ombre_ellipse(taille, largeur_rel, hauteur_rel, bas_rel, alpha):
    """Petite ombre ovale douce posée au sol."""
    s = pygame.Surface((taille, taille), pygame.SRCALPHA)
    w, h = int(taille * largeur_rel), max(2, int(taille * hauteur_rel))
    rect = pygame.Rect(0, 0, w, h)
    rect.center = (taille // 2, int(taille * bas_rel))
    for k in range(3):                              # 3 couches = bord doux
        r = rect.inflate(-k * max(2, w // 8), -k * max(1, h // 4))
        pygame.draw.ellipse(s, (0, 0, 0, alpha // 3 + k * alpha // 3), r)
    return s


def halo(taille, couleur, force):
    """Halo lumineux circulaire (dégradé de transparence)."""
    s = pygame.Surface((taille, taille), pygame.SRCALPHA)
    c = taille // 2
    for r in range(c, 0, -1):
        a = int(force * (1 - r / c) ** 2)
        pygame.draw.circle(s, (*couleur, a), (c, c), r)
    return s


# ----------------------------------------------------------------------
# Dessin (donjon de pierre, sol en bois, caisses, petit héros)
# ----------------------------------------------------------------------
def dessiner_fond(ecran):
    """Fond dégradé nuit violette avec quelques étoiles."""
    largeur, hauteur = ecran.get_size()

    def fabriquer():
        s = pygame.Surface((largeur, hauteur))
        for y in range(hauteur):
            t = y / max(1, hauteur - 1)
            couleur = tuple(int(C_FOND_HAUT[k] + (C_FOND_BAS[k] - C_FOND_HAUT[k]) * t)
                            for k in range(3))
            pygame.draw.line(s, couleur, (0, y), (largeur, y))
        hasard = random.Random(7)                   # étoiles toujours au même endroit
        for _ in range(largeur * hauteur // 9000):
            x, y = hasard.randrange(largeur), hasard.randrange(hauteur)
            lum = hasard.randrange(90, 200)
            s.set_at((x, y), (lum, lum, min(255, lum + 30)))
        return s

    ecran.blit(en_cache(('fond', largeur, hauteur), fabriquer), (0, 0))


def dessiner_mur(ecran, rect):
    """Mur en pierre : briques nuancées avec reflets et joints sombres."""
    t = rect.w

    def fabriquer():
        s = pygame.Surface((t, t))
        s.fill(C_MORTIER)
        lignes = 3
        haut = t / lignes
        for k in range(lignes):
            y0, y1 = int(k * haut), int((k + 1) * haut)
            larg = t / 2
            decalage = 0 if k % 2 == 0 else -larg / 2
            for m in range(-1, 3):
                x0 = int(m * larg + decalage)
                x1 = int(x0 + larg)
                r = pygame.Rect(x0 + 1, y0 + 1, x1 - x0 - 1, y1 - y0 - 1).clip(s.get_rect())
                if r.w <= 1 or r.h <= 1:
                    continue
                couleur = nuance(C_PIERRE, ((k * 7 + m * 5) % 4) * 7 - 12)
                pygame.draw.rect(s, couleur, r)
                pygame.draw.line(s, nuance(couleur, 34), r.topleft, (r.right - 1, r.top))
                pygame.draw.line(s, nuance(couleur, -38), (r.left, r.bottom - 1),
                                 (r.right - 1, r.bottom - 1))
        pygame.draw.rect(s, nuance(C_MORTIER, -18), s.get_rect(), 1)
        return s

    ecran.blit(en_cache(('mur', t), fabriquer), rect.topleft)


def dessiner_sol(ecran, rect):
    """Sol en parquet : deux planches par case, légèrement différentes."""
    t = rect.w
    variante = ((rect.x // t) * 3 + (rect.y // t) * 5) % 4

    def fabriquer():
        s = pygame.Surface((t, t))
        for k in range(2):
            plank = pygame.Rect(0, k * t // 2, t, t - (t // 2) * 1 if k else t // 2)
            couleur = nuance(C_BOIS_SOL, ((variante + k * 2) % 4) * 6 - 10)
            pygame.draw.rect(s, couleur, plank)
            pygame.draw.line(s, nuance(couleur, 22), plank.topleft, (plank.right, plank.top))
            pygame.draw.line(s, nuance(couleur, -46), (0, plank.bottom - 1),
                             (t, plank.bottom - 1))
            # petit joint vertical à un endroit qui change d'une planche à l'autre
            xj = (variante * t // 4 + k * t // 3 + t // 5) % t
            pygame.draw.line(s, nuance(couleur, -34), (xj, plank.top), (xj, plank.bottom - 1))
            # veines du bois
            for v in range(2):
                yv = plank.top + (v + 1) * plank.h // 3
                xv = (xj + (v + 1) * t // 3) % max(1, t - t // 3)
                pygame.draw.line(s, nuance(couleur, -14), (xv, yv), (xv + t // 3, yv))
        return s

    ecran.blit(en_cache(('sol', t, variante), fabriquer), rect.topleft)


def dessiner_cible(ecran, rect):
    """Rune lumineuse bleue qui pulse doucement."""
    t = rect.w
    pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 380.0)

    lueur = en_cache(('lueur', t), lambda: halo(t, C_CIBLE_GLOW, 200))
    lueur.set_alpha(int(110 + 145 * pulse))
    ecran.blit(lueur, rect.topleft)

    def fabriquer():
        s = pygame.Surface((t, t), pygame.SRCALPHA)
        c = t // 2
        r = int(t * 0.30)
        losange = [(c, c - r), (c + r, c), (c, c + r), (c - r, c)]
        pygame.draw.polygon(s, (*C_CIBLE_GLOW, 255), losange, max(2, t // 22))
        r2 = int(t * 0.15)
        pygame.draw.polygon(s, (255, 255, 255, 235),
                            [(c, c - r2), (c + r2, c), (c, c + r2), (c - r2, c)])
        return s

    ecran.blit(en_cache(('rune', t), fabriquer), rect.topleft)


def dessiner_caisse(ecran, rect, sur_cible):
    """Caisse en bois cerclée de fer (dorée et lumineuse sur une cible)."""
    t = rect.w
    if sur_cible:
        pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 450.0)
        lueur = en_cache(('lueur_or', t), lambda: halo(t, C_CAISSE_OR, 170))
        lueur.set_alpha(int(120 + 120 * pulse))
        ecran.blit(lueur, rect.topleft)

    ecran.blit(en_cache(('ombre_caisse', t), lambda: ombre_ellipse(t, 0.86, 0.16, 0.92, 120)),
               rect.topleft)

    def fabriquer():
        s = pygame.Surface((t, t), pygame.SRCALPHA)
        corps = pygame.Rect(0, 0, int(t * 0.80), int(t * 0.80))
        corps.center = (t // 2, int(t * 0.50))
        base = C_CAISSE_OR if sur_cible else C_CAISSE
        bord = C_CAISSE_OR_BORD if sur_cible else C_CAISSE_BORD
        epais = max(3, t // 9)

        pygame.draw.rect(s, bord, corps, border_radius=max(2, t // 16))
        interieur = corps.inflate(-2 * epais, -2 * epais)
        pygame.draw.rect(s, base, interieur)
        for k in range(1, 4):                               # planches
            y = interieur.y + k * interieur.h // 4
            pygame.draw.line(s, nuance(base, -46), (interieur.x, y), (interieur.right, y))
            pygame.draw.line(s, nuance(base, 26), (interieur.x, y + 1),
                             (interieur.right, y + 1))
        pygame.draw.line(s, nuance(base, 36), interieur.topleft,                # croix
                         (interieur.right, interieur.bottom), max(2, t // 16))
        pygame.draw.line(s, nuance(base, 36), interieur.bottomleft,
                         (interieur.right, interieur.top), max(2, t // 16))
        pygame.draw.rect(s, nuance(bord, 30), corps, 1, border_radius=max(2, t // 16))
        pygame.draw.line(s, nuance(base, 60), (corps.x + 2, corps.y + 1),        # reflet haut
                         (corps.right - 3, corps.y + 1), 1)
        for cx, cy in (corps.topleft, corps.topright, corps.bottomleft, corps.bottomright):
            dx = epais // 2 + 1 if cx == corps.left else -(epais // 2 + 1)
            dy = epais // 2 + 1 if cy == corps.top else -(epais // 2 + 1)
            pygame.draw.circle(s, nuance(base, 70), (cx + dx, cy + dy), max(1, t // 32))
        return s

    ecran.blit(en_cache(('caisse', t, sur_cible), fabriquer), rect.topleft)


def dessiner_joueur(ecran, rect):
    """Petit héros : bonnet rouge, veste bleue, bottes, avec une ombre."""
    t = rect.w
    ecran.blit(en_cache(('ombre_joueur', t), lambda: ombre_ellipse(t, 0.60, 0.14, 0.90, 130)),
               rect.topleft)

    def fabriquer():
        s = pygame.Surface((t, t), pygame.SRCALPHA)
        cx = t // 2
        u = t / 10
        # bottes et jambes
        for dx in (-1.1, 0.1):
            pygame.draw.rect(s, C_BOTTES, (cx + dx * u, 8.0 * u, 1.0 * u, 1.0 * u),
                             border_radius=max(1, int(u / 3)))
            pygame.draw.rect(s, C_PANTALON, (cx + dx * u, 6.9 * u, 1.0 * u, 1.3 * u))
        # corps (veste)
        corps = pygame.Rect(cx - 1.9 * u, 4.2 * u, 3.8 * u, 3.0 * u)
        pygame.draw.rect(s, C_VESTE, corps, border_radius=max(2, int(u)))
        pygame.draw.rect(s, nuance(C_VESTE, 40), (corps.x + 2, corps.y + 2, corps.w - 4, 2),
                         border_radius=1)
        pygame.draw.line(s, nuance(C_VESTE, -50), (cx, corps.y + 3), (cx, corps.bottom - 2), 1)
        # bras
        for dx in (-2.3, 1.8):
            pygame.draw.rect(s, nuance(C_VESTE, -20), (cx + dx * u, 4.5 * u, 0.55 * u, 2.2 * u),
                             border_radius=max(1, int(u / 3)))
            pygame.draw.circle(s, C_PEAU, (int(cx + (dx + 0.27) * u), int(6.9 * u)),
                               max(1, int(u * 0.35)))
        # tête
        pygame.draw.circle(s, C_PEAU, (cx, int(3.0 * u)), int(1.9 * u))
        # bonnet
        pygame.draw.circle(s, C_BONNET, (cx, int(2.6 * u)), int(1.95 * u))
        pygame.draw.rect(s, C_PEAU, (cx - 2.1 * u, 2.65 * u, 4.2 * u, 2.2 * u))
        pygame.draw.circle(s, C_PEAU, (cx, int(3.0 * u)), int(1.7 * u))
        pygame.draw.arc(s, C_BONNET, (cx - 2.0 * u, 0.9 * u, 4.0 * u, 3.4 * u), 0.0, math.pi,
                        max(2, int(u * 0.9)))
        pygame.draw.circle(s, (250, 250, 250), (int(cx + 1.6 * u), int(1.7 * u)),
                           max(1, int(u * 0.45)))                              # pompon
        # yeux et joues
        for dx in (-0.75, 0.75):
            pygame.draw.circle(s, C_CHEVEUX, (int(cx + dx * u), int(3.2 * u)), max(1, int(u / 3)))
            pygame.draw.circle(s, (245, 150, 140), (int(cx + dx * 1.7 * u), int(3.8 * u)),
                               max(1, int(u / 3.5)))
        return s

    ecran.blit(en_cache(('joueur', t), fabriquer), rect.topleft)


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


def ecrire(ecran, police, texte, x, y, couleur=C_TEXTE, gras=False, espace=6):
    """Écrit une ligne de texte et retourne la ordonnée de la ligne suivante."""
    police.set_bold(gras)
    surface = police.render(texte, True, couleur)
    police.set_bold(False)
    ecran.blit(surface, (x, y))
    return y + surface.get_height() + espace


def carte(ecran, rect, fond, bordure=None, rayon=10):
    """Rectangle arrondi (fond + fine bordure) pour structurer le panneau."""
    pygame.draw.rect(ecran, fond, rect, border_radius=rayon)
    if bordure is not None:
        pygame.draw.rect(ecran, bordure, rect, 1, border_radius=rayon)


def draw_info(ecran, polices, x, infos):
    """Panneau latéral : algorithme, coût, nœuds, comparaison, contrôles."""
    police, petite = polices
    largeur_ecran, hauteur_ecran = ecran.get_size()
    panneau = pygame.Rect(x - 8, 10, largeur_ecran - x - 2, hauteur_ecran - 20)
    carte(ecran, panneau, C_PANNEAU, C_PANNEAU_BORD, 14)

    xi = panneau.x + 16                    # marge gauche du contenu
    largeur_i = panneau.w - 32
    couleur_algo = C_ALGOS[infos['algo_idx'] % len(C_ALGOS)]

    y = panneau.y + 14
    y = ecrire(ecran, police, f"Niveau : {infos['nom']}", xi, y, C_OR, gras=True, espace=8)

    # pastille de l'algorithme affiché
    pastille = pygame.Rect(xi, y, largeur_i, 30)
    carte(ecran, pastille, nuance(couleur_algo, -105), couleur_algo, 15)
    texte = police.render(f"Algorithme : {infos['algo']}", True, C_TEXTE)
    ecran.blit(texte, texte.get_rect(center=pastille.center))
    y = pastille.bottom + 10

    # carte des statistiques
    lignes = []
    if infos['solution'] is None:
        lignes.append(("Pas de solution", C_ERREUR))
    else:
        lignes.append((f"Coût : {infos['cout']}", C_TEXTE))
        lignes.append((f"Étape : {infos['etape']} / {infos['total']}", C_TEXTE))
    lignes.append((f"Nœuds explorés : {infos['noeuds']}", C_TEXTE))
    lignes.append((f"Délai : {infos['delai']} ms", C_TEXTE_GRIS))
    hauteur_carte = 12 + len(lignes) * 26 + 22 + 28
    zone = pygame.Rect(xi - 6, y, largeur_i + 12, hauteur_carte)
    carte(ecran, zone, C_CARTE, None, 10)
    yy = y + 10
    for texte, couleur in lignes:
        yy = ecrire(ecran, police, texte, xi + 4, yy, couleur, espace=2)
    # barre de progression
    if infos['solution'] is not None and infos['total'] > 0:
        ratio = infos['etape'] / infos['total']
    else:
        ratio = 0
    barre = pygame.Rect(xi + 4, yy + 6, largeur_i - 8, 10)
    pygame.draw.rect(ecran, nuance(C_CARTE, -22), barre, border_radius=5)
    if ratio > 0:
        plein = barre.copy()
        plein.w = max(10, int(barre.w * ratio))
        pygame.draw.rect(ecran, couleur_algo, plein, border_radius=5)
    yy = barre.bottom + 8
    etat_txt = "EN PAUSE" if infos['pause'] else "Lecture"
    couleur_etat = C_OR if infos['pause'] else (120, 220, 150)
    ecran.blit(petite.render(etat_txt, True, couleur_etat), (xi + 4, yy))
    touche = petite.render(f"Touche : {infos['touche']}", True, C_TEXTE_GRIS)
    ecran.blit(touche, (zone.right - touche.get_width() - 10, yy))
    y = zone.bottom + 12

    # tableau comparatif de toutes les méthodes
    y = ecrire(ecran, petite, "Comparaison (coût | nœuds | temps)", xi, y, C_OR, gras=True,
               espace=4)
    plus_grand = max([r['noeuds'] for r in infos['resultats']] + [1])
    for k, r in enumerate(infos['resultats']):
        ligne = pygame.Rect(xi - 6, y, largeur_i + 12, 30)
        actif = (k == infos['algo_idx'])
        couleur = C_ALGOS[k % len(C_ALGOS)]
        carte(ecran, ligne, nuance(couleur, -100) if actif else C_CARTE,
              couleur if actif else None, 8)
        cout = r['cout'] if r['solution'] is not None else "-"
        c_txt = C_TEXTE if actif else C_TEXTE_GRIS
        ecran.blit(petite.render(f"{r['algo']}", True, c_txt), (ligne.x + 8, ligne.y + 2))
        resume = petite.render(f"{cout} | {r['noeuds']} | {r['temps']:.2f}s", True, c_txt)
        ecran.blit(resume, (ligne.right - resume.get_width() - 8, ligne.y + 2))
        longueur = int((ligne.w - 16) * r['noeuds'] / plus_grand)
        pygame.draw.rect(ecran, couleur if actif else nuance(couleur, -70),
                         (ligne.x + 8, ligne.bottom - 7, max(3, longueur), 3), border_radius=2)
        y += 34

    # aide des touches
    y += 4
    for ligne in ("TAB : changer d'algorithme",
                  "ESPACE : pause / reprise",
                  "Flèches (ou D / Q) : pas à pas",
                  "R : recommencer",
                  "+ ou F : accélérer",
                  "- ou L : ralentir",
                  "N : niveau suivant",
                  "ECHAP : quitter"):
        y = ecrire(ecran, petite, ligne, xi, y, C_TEXTE_GRIS, espace=1)


def dessiner_tout(ecran, polices, etat, taille, infos):
    """Redessine la fenêtre complète."""
    dessiner_fond(ecran)
    # tapis sombre sous la grille pour la détacher du fond
    draw_board(ecran, etat, taille)
    draw_info(ecran, polices, etat.width * taille + 15, infos)
    if infos['solution'] is None:
        # bandeau bien visible au centre de la grille
        msg = polices[0].render("Pas de solution", True, C_ERREUR)
        centre = (etat.width * taille // 2, etat.height * taille // 2)
        bande = msg.get_rect(center=centre).inflate(40, 22)
        fond = pygame.Surface(bande.size, pygame.SRCALPHA)
        pygame.draw.rect(fond, (20, 10, 20, 215), fond.get_rect(), border_radius=12)
        pygame.draw.rect(fond, (*C_ERREUR, 255), fond.get_rect(), 2, border_radius=12)
        ecran.blit(fond, bande.topleft)
        ecran.blit(msg, msg.get_rect(center=centre))
    pygame.display.flip()


# ----------------------------------------------------------------------
# Programme principal
# ----------------------------------------------------------------------
def charger_niveau(index, polices):
    """Prépare un niveau : fenêtre + toutes les recherches. Retourne un dictionnaire."""
    nom, grille = NIVEAUX[index]
    initial = creer_etat_initial(grille)
    ecran, taille = creer_fenetre(initial)
    resultats = lancer_recherches(ecran, polices[0], initial)
    return {'nom': nom, 'ecran': ecran, 'taille': taille, 'resultats': resultats}


def touche_est(event, touches, caractere=None):
    """Vrai si la touche pressée est dans `touches` (ou produit ce caractère)."""
    return event.key in touches or (caractere is not None and event.unicode == caractere)


def main():
    pygame.init()
    pygame.display.set_caption("Sokoban - BFS et A*")
    polices = (pygame.font.SysFont("arial", 22), pygame.font.SysFont("arial", 17))
    horloge = pygame.time.Clock()

    index = 0
    algo = 0                                    # indice de la méthode affichée
    niveau = charger_niveau(index, polices)
    etape = 0
    delai = DELAI_DEFAUT
    pause = False
    dernier_pas = pygame.time.get_ticks()
    derniere_touche = '-'
    en_cours = True

    while en_cours:
        res = niveau['resultats'][algo]
        total = len(res['chemin']) - 1          # nombre de coups
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
            elif event.type == pygame.KEYDOWN:
                derniere_touche = pygame.key.name(event.key)
                if event.key == pygame.K_ESCAPE:
                    en_cours = False
                elif event.key == pygame.K_TAB:
                    algo = (algo + 1) % len(METHODES)
                    etape, pause = 0, False
                    dernier_pas = pygame.time.get_ticks()
                elif event.key == pygame.K_SPACE:
                    pause = not pause
                elif touche_est(event, (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN)):
                    etape, pause = min(etape + 1, total), True
                elif touche_est(event, (pygame.K_LEFT, pygame.K_q, pygame.K_a, pygame.K_UP)):
                    etape, pause = max(etape - 1, 0), True
                elif event.key == pygame.K_r:
                    etape, pause = 0, False
                    dernier_pas = pygame.time.get_ticks()
                elif touche_est(event, (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS,
                                        pygame.K_f), '+'):
                    delai = max(DELAI_MIN, delai - PAS_DELAI)
                elif touche_est(event, (pygame.K_MINUS, pygame.K_KP_MINUS, pygame.K_l,
                                        pygame.K_6), '-'):
                    delai = min(DELAI_MAX, delai + PAS_DELAI)
                elif event.key == pygame.K_n:
                    index = (index + 1) % len(NIVEAUX)
                    niveau = charger_niveau(index, polices)
                    algo = 0
                    etape, pause = 0, False
                    dernier_pas = pygame.time.get_ticks()
                    res = niveau['resultats'][algo]
                    total = len(res['chemin']) - 1

        # avance automatique toutes les `delai` millisecondes
        maintenant = pygame.time.get_ticks()
        if not pause and etape < total and maintenant - dernier_pas >= delai:
            etape += 1
            dernier_pas = maintenant

        infos = {'nom': niveau['nom'], 'algo': res['algo'],
                 'solution': res['solution'], 'cout': res['cout'],
                 'noeuds': res['noeuds'], 'etape': etape, 'total': total,
                 'delai': delai, 'pause': pause, 'touche': derniere_touche,
                 'resultats': niveau['resultats'], 'algo_idx': algo}
        dessiner_tout(niveau['ecran'], polices, res['chemin'][etape],
                      niveau['taille'], infos)
        horloge.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()