# ============================================================
# abr.py - Arbre Binaire de Recherche (ABR) pour LowBid
# Structure centrale du projet : chaque nœud = un prix
# avec la liste des joueurs ayant proposé ce prix
# ============================================================


class Noeud:
    """
    Représente un nœud de l'Arbre Binaire de Recherche.
    Clé du nœud : le prix proposé (entier >= 0).
    Valeur associée : liste des joueurs ayant proposé ce prix.
    """

    def __init__(self, prix, joueur):
        """
        Crée un nouveau nœud avec un prix et son premier joueur.
        prix   : entier >= 0, la clé du nœud
        joueur : identifiant du joueur (ex : "J01")
        """
        self.prix    = prix         # La clé du nœud (entier représentant le prix)
        self.joueurs = [joueur]     # Liste des joueurs ayant misé ce prix (au moins 1 au départ)
        self.gauche  = None         # Référence vers le fils gauche (prix inférieurs)
        self.droite  = None         # Référence vers le fils droit (prix supérieurs)


class ABR:
    """
    Arbre Binaire de Recherche pour gérer les mises d'une enchère LowBid.
    Propriété ABR : pour tout nœud N, tous les prix du sous-arbre gauche < N.prix,
    et tous les prix du sous-arbre droit > N.prix.
    Plusieurs joueurs peuvent avoir le même prix : ils sont stockés dans une liste.
    """

    def __init__(self):
        """
        Initialise un ABR vide.
        """
        self.racine = None  # La racine est None tant qu'aucune mise n'a été insérée

    def inserer(self, prix, joueur):
        """
        Insère une mise (prix d'un joueur) dans l'ABR.
        Si le prix existe déjà dans l'arbre, le joueur est ajouté à la liste du nœud.
        Sinon, un nouveau nœud est créé.
        Complexité moyenne : O(log n) | pire cas : O(n) si l'arbre est dégénéré
        """
        if self.racine is None:
            self.racine = Noeud(prix, joueur)
        else:
            self._inserer_rec(self.racine, prix, joueur)

    def _inserer_rec(self, noeud, prix, joueur):
        if prix == noeud.prix:
            if joueur not in noeud.joueurs:
                noeud.joueurs.append(joueur)
        elif prix < noeud.prix:
            if noeud.gauche is None:
                noeud.gauche = Noeud(prix, joueur)
            else:
                self._inserer_rec(noeud.gauche, prix, joueur)
        else:
            if noeud.droite is None:
                noeud.droite = Noeud(prix, joueur)
            else:
                self._inserer_rec(noeud.droite, prix, joueur)

    def parcours_infixe(self):
        """
        Retourne la liste de TOUS les nœuds dans l'ordre CROISSANT des prix.
        Le parcours infixe d'un ABR donne toujours les clés dans l'ordre trié.
        Complexité : O(n).
        """
        resultat = []
        self._infixe_rec(self.racine, resultat)
        return resultat

    def _infixe_rec(self, noeud, resultat):
        """Parcours infixe récursif : gauche -> noeud courant -> droite."""
        if noeud is None:
            return
        self._infixe_rec(noeud.gauche, resultat)   # 1) Visiter le sous-arbre GAUCHE
        resultat.append(noeud)                     # 2) Ajouter le nœud COURANT
        self._infixe_rec(noeud.droite, resultat)   # 3) Visiter le sous-arbre DROIT

    def trouver_plus_bas_unique(self):
        """
        Trouve le plus petit prix proposé par exactement UN seul joueur.
        C'est la clé du jeu LowBid : le gagnant est celui qui a le plus bas prix unique.
        Retourne le nœud gagnant, ou None si aucun prix n'est unique.
        Complexité : O(n) dans le pire cas.
        """
        noeuds_tries = self.parcours_infixe()  # Tous les nœuds triés par prix croissant
        for noeud in noeuds_tries:
            if len(noeud.joueurs) == 1:
                return noeud  # Premier prix unique = gagnant
        return None  # Aucun prix unique : manche annulée

    def rechercher(self, prix):
        """Recherche un nœud par son prix. Retourne le nœud ou None."""
        return self._rechercher_rec(self.racine, prix)

    def _rechercher_rec(self, noeud, prix):
        """Recherche récursive dans l'ABR."""
        if noeud is None:
            return None  # Prix non trouvé
        if prix == noeud.prix:
            return noeud  # Trouvé !
        elif prix < noeud.prix:
            return self._rechercher_rec(noeud.gauche, prix)  # Chercher à gauche
        else:
            return self._rechercher_rec(noeud.droite, prix)  # Chercher à droite

    def successeur(self, prix):
        """
        Retourne le nœud avec le plus petit prix STRICTEMENT supérieur à 'prix'.
        Utile pour trouver le prochain candidat après un prix non unique.
        Complexité : O(h) où h = hauteur de l'arbre.
        """
        successeur = None
        noeud = self.racine
        while noeud is not None:
            if noeud.prix > prix:
                successeur = noeud       # Candidat valide
                noeud = noeud.gauche     # Cherche un candidat encore plus petit
            else:
                noeud = noeud.droite     # Prix trop petit : va à droite
        return successeur

    def predecesseur(self, prix):
        """
        Retourne le nœud avec le plus grand prix STRICTEMENT inférieur à 'prix'.
        Utile pour naviguer dans l'ordre des prix.
        Complexité : O(h) où h = hauteur de l'arbre.
        """
        predecesseur = None
        noeud = self.racine
        while noeud is not None:
            if noeud.prix < prix:
                predecesseur = noeud     # Candidat valide
                noeud = noeud.droite     # Cherche un candidat encore plus grand
            else:
                noeud = noeud.gauche     # Prix trop grand : va à gauche
        return predecesseur

    def nb_total_mises(self):
        """Retourne le nombre total de mises (somme des joueurs dans chaque nœud)."""
        total = 0
        for noeud in self.parcours_infixe():
            total += len(noeud.joueurs)  # On additionne le nb de joueurs par nœud
        return total

    def distribution_prix(self):
        """Retourne {prix: nb_joueurs} dans l'ordre croissant des prix."""
        distribution = {}
        for noeud in self.parcours_infixe():
            distribution[noeud.prix] = len(noeud.joueurs)
        return distribution

    def afficher_etat(self):
        """Affiche l'état de l'enchère (parcours infixe = prix triés)."""
        noeuds = self.parcours_infixe()
        if not noeuds:
            print("L'enchère est vide.")
            return
        print("=" * 55)
        print("  ETAT DE L'ENCHERE (prix croissants)")
        print("=" * 55)
        for noeud in noeuds:
            if len(noeud.joueurs) == 1:
                indicateur = "UNIQUE"  # Ce prix n'appartient qu'à un joueur
            else:
                indicateur = f"({len(noeud.joueurs)} joueurs)"
            print(f"  Prix {noeud.prix:4d}  ->  {noeud.joueurs}  {indicateur}")
        print("=" * 55)

    def est_vide(self):
        """Retourne True si l'ABR est vide, False sinon."""
        return self.racine is None  # Vide si et seulement si la racine est None

    def hauteur(self):
        """
        Retourne la hauteur de l'ABR.
        Un ABR équilibré a une hauteur ~log2(n).
        Un ABR dégénéré (insertions triées) a une hauteur = n.
        """
        return self._hauteur_rec(self.racine)

    def _hauteur_rec(self, noeud):
        """Calcul récursif de la hauteur : 1 + max(gauche, droite)."""
        if noeud is None:
            return 0  # Arbre vide = hauteur 0
        hauteur_gauche = self._hauteur_rec(noeud.gauche)
        hauteur_droite = self._hauteur_rec(noeud.droite)
        return 1 + max(hauteur_gauche, hauteur_droite)  # Hauteur = 1 + max des deux sous-arbres
