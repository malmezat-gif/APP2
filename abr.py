class Noeud:
    """
    Un noeud represente un prix dans l'arbre.

    On stocke :
    - le prix
    - la liste des joueurs qui ont choisi ce prix
    - le fils gauche
    - le fils droit
    """

    def __init__(self, prix, joueur):
        self.prix = prix
        self.joueurs = [joueur]
        self.gauche = None
        self.droite = None


class ABR:
    """
    ABR simple pour garder les prix dans l'ordre.

    Regle :
    - a gauche il y a les prix plus petits
    - a droite il y a les prix plus grands
    """

    def __init__(self):
        self.racine = None

    def est_vide(self):
        """Retourne True si aucune mise n'a encore ete inseree."""
        return self.racine is None

    def inserer(self, prix, joueur):
        """
        Ajoute une mise dans l'arbre.

        Dans l'ordre :
        - si l'arbre est vide, on cree la racine
        - sinon on descend a gauche ou a droite
        - si le prix existe deja, on ajoute le joueur dans la liste
        """
        if self.racine is None:
            self.racine = Noeud(prix, joueur)
            return

        self._inserer(self.racine, prix, joueur)

    def _inserer(self, noeud, prix, joueur):
        if prix == noeud.prix:
            if joueur not in noeud.joueurs:
                noeud.joueurs.append(joueur)
            return

        if prix < noeud.prix:
            if noeud.gauche is None:
                noeud.gauche = Noeud(prix, joueur)
            else:
                self._inserer(noeud.gauche, prix, joueur)
            return

        if noeud.droite is None:
            noeud.droite = Noeud(prix, joueur)
        else:
            self._inserer(noeud.droite, prix, joueur)

    def rechercher(self, prix):
        """
        Cherche un prix dans l'arbre.

        On compare le prix cherche avec le noeud courant
        jusqu'a le trouver ou jusqu'a tomber sur None.
        """
        noeud = self.racine

        while noeud is not None:
            if prix == noeud.prix:
                return noeud
            if prix < noeud.prix:
                noeud = noeud.gauche
            else:
                noeud = noeud.droite

        return None

    def parcours_infixe(self):
        """
        Retourne les noeuds dans l'ordre croissant des prix.

        Le parcours infixe fait :
        gauche -> noeud -> droite
        """
        resultat = []
        self._parcours_infixe(self.racine, resultat)
        return resultat

    def _parcours_infixe(self, noeud, resultat):
        if noeud is None:
            return

        self._parcours_infixe(noeud.gauche, resultat)
        resultat.append(noeud)
        self._parcours_infixe(noeud.droite, resultat)

    def trouver_plus_bas_unique(self):
        """
        Cherche le premier prix unique.

        Comme le parcours infixe donne les prix tries,
        le premier noeud avec un seul joueur est le gagnant.
        """
        for noeud in self.parcours_infixe():
            if len(noeud.joueurs) == 1:
                return noeud
        return None

    def successeur(self, prix):
        """
        Cherche le premier prix strictement plus grand.

        On garde un candidat pendant qu'on descend dans l'arbre.
        """
        candidat = None
        noeud = self.racine

        while noeud is not None:
            if noeud.prix > prix:
                candidat = noeud
                noeud = noeud.gauche
            else:
                noeud = noeud.droite

        return candidat

    def predecesseur(self, prix):
        """
        Cherche le premier prix strictement plus petit.

        Le principe est le meme que pour le successeur,
        mais en sens inverse.
        """
        candidat = None
        noeud = self.racine

        while noeud is not None:
            if noeud.prix < prix:
                candidat = noeud
                noeud = noeud.droite
            else:
                noeud = noeud.gauche

        return candidat

    def nb_total_mises(self):
        """Compte toutes les mises, meme quand un prix est partage."""
        total = 0
        for noeud in self.parcours_infixe():
            total += len(noeud.joueurs)
        return total

    def distribution_prix(self):
        """Retourne un dictionnaire {prix: nombre_de_joueurs}."""
        distribution = {}
        for noeud in self.parcours_infixe():
            distribution[noeud.prix] = len(noeud.joueurs)
        return distribution

    def hauteur(self):
        """
        Donne la hauteur de l'arbre.

        Un arbre trop haut pour peu de noeuds peut etre degenerate.
        """
        return self._hauteur(self.racine)

    def _hauteur(self, noeud):
        if noeud is None:
            return 0

        hauteur_gauche = self._hauteur(noeud.gauche)
        hauteur_droite = self._hauteur(noeud.droite)
        return 1 + max(hauteur_gauche, hauteur_droite)

    def supprimer_joueur(self, prix, joueur):
        """
        Supprime une mise precise.

        Etapes :
        - on cherche le noeud du prix
        - on retire le joueur de la liste
        - si la liste devient vide, on retire le noeud de l'ABR
        """
        noeud = self.rechercher(prix)

        if noeud is None or joueur not in noeud.joueurs:
            return False

        noeud.joueurs.remove(joueur)

        if not noeud.joueurs:
            self.racine = self._supprimer_noeud(self.racine, prix)

        return True

    def _supprimer_noeud(self, noeud, prix):
        """
        Supprime un noeud de l'ABR.

        Cas geres :
        - pas d'enfant
        - un seul enfant
        - deux enfants
        """
        if noeud is None:
            return None

        if prix < noeud.prix:
            noeud.gauche = self._supprimer_noeud(noeud.gauche, prix)
            return noeud

        if prix > noeud.prix:
            noeud.droite = self._supprimer_noeud(noeud.droite, prix)
            return noeud

        if noeud.gauche is None:
            return noeud.droite

        if noeud.droite is None:
            return noeud.gauche

        remplacant = self._minimum(noeud.droite)
        noeud.prix = remplacant.prix
        noeud.joueurs = remplacant.joueurs[:]
        noeud.droite = self._supprimer_noeud(noeud.droite, remplacant.prix)
        return noeud

    def _minimum(self, noeud):
        """Descend a gauche jusqu'au plus petit prix du sous-arbre."""
        courant = noeud
        while courant.gauche is not None:
            courant = courant.gauche
        return courant
