class Node:
    
    
    def __init__(self, state, parent=None, action=None):
        self.state = state      # l'etat du jeu 
        self.parent = parent    # le noeud d'avant 
        self.action = action    # le mouvement qui nous a amenes ici 

        # g = nombre de pas depuis le depart (chaque pas coute 1)
        if parent is None:
            self.g = 0
        else:
            self.g = parent.g + 1


    def getPath(self):
        """Renvoie la liste des etats, du depart jusqu'a ce noeud."""
        chemin = []
        noeud = self
        while noeud is not None:
            chemin.append(noeud.state)
            noeud = noeud.parent
        chemin.reverse()  
        return chemin 

    def getSolution(self):
        """Renvoie la liste des actions (U, D, L, R) du depart jusqu'a ce noeud."""
        actions = []
        noeud = self
        
        while noeud.parent is not None:
            actions.append(noeud.action)
            noeud = noeud.parent
        actions.reverse()
        return actions

