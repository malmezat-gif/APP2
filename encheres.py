# ============================================================
# encheres.py - Moteur d'enchère LowBid "Qui perd gagne !"
# Gère une manche complète : chargement, calcul des coûts,
# recherche du gagnant et recette du vendeur.
# ============================================================

from abr import ABR           # Notre structure Arbre Binaire de Recherche
from outils import cout_mise  # Fonction de calcul du coût d'une mise


class Enchere:
    """
    Représente une manche d'enchère LowBid.
    Utilise un ABR pour stocker et analyser les mises efficacement.
    """

    def __init__(self, cout_base=1, alpha=10):
        """
        Initialise une manche vide avec les paramètres de coût.
        cout_base : coût fixe appliqué à chaque mise (en euros)
        alpha     : paramètre d'intensité de la prime de risque
        """
        self.abr       = ABR()       # L'arbre binaire de recherche qui stocke toutes les mises
        self.cout_base = cout_base   # Coût fixe de participation
        self.alpha     = alpha       # Prime de risque
        self.mises     = []          # Liste brute des mises : [(joueur, prix), ...]

    def ajouter_mise(self, joueur, prix):
        """
        Enregistre la mise d'un joueur.
        Insère dans l'ABR ET conserve une copie dans la liste brute.
        Un prix négatif est refusé (règle du jeu).
        """
        if prix < 0:
            print(f"[Erreur] Prix invalide ({prix}) - doit être >= 0.")
            return
        self.mises.append((joueur, prix))  # Sauvegarde dans la liste brute
        self.abr.inserer(prix, joueur)     # Insertion dans l'ABR

    def charger_depuis_liste(self, liste_mises):
        """
        Charge des mises depuis une liste de tuples.
        Format accepté : (joueur, prix) ou (manche, joueur, prix).
        """
        for mise in liste_mises:
            if len(mise) == 2:
                joueur, prix = mise          # Format simple
                self.ajouter_mise(joueur, prix)
            elif len(mise) == 3:
                _, joueur, prix = mise       # On ignore le numéro de manche
                self.ajouter_mise(joueur, prix)

    def trouver_gagnant(self):
        """
        Détermine le gagnant : joueur avec le PLUS BAS PRIX UNIQUE.
        Retourne (prix, joueur) ou None si aucun gagnant.
        """
        noeud_gagnant = self.abr.trouver_plus_bas_unique()  # Recherche dans l'ABR
        if noeud_gagnant is None:
            return None  # Aucun prix unique : manche annulée
        return (noeud_gagnant.prix, noeud_gagnant.joueurs[0])  # (prix gagnant, joueur gagnant)

    def calculer_cout_joueur(self, joueur):
        """
        Calcule le coût total payé par un joueur dans cette manche.
        Somme de cout_mise(prix) pour chaque mise du joueur.
        """
        cout_total = 0.0
        for (j, prix) in self.mises:
            if j == joueur:
                cout_total += cout_mise(prix, self.cout_base, self.alpha)  # Coût de cette mise
        return round(cout_total, 2)

    def calculer_recette_vendeur(self):
        """
        Calcule la recette totale du vendeur (somme des coûts de toutes les mises).
        Le vendeur encaisse même si la manche est annulée.
        """
        recette = 0.0
        for (joueur, prix) in self.mises:
            recette += cout_mise(prix, self.cout_base, self.alpha)  # Coût de chaque mise
        return round(recette, 2)

    def calculer_cout_moyen_par_joueur(self):
        """
        Calcule le coût moyen par joueur : recette totale / nb joueurs distincts.
        """
        if not self.mises:
            return 0.0
        joueurs_uniques = set(j for (j, _) in self.mises)  # Joueurs sans doublons
        cout_total = self.calculer_recette_vendeur()
        return round(cout_total / len(joueurs_uniques), 2)

    def afficher_resultats(self):
        """Affiche un résumé complet de la manche dans la console."""
        print("\n" + "=" * 55)
        print("  RESULTATS DE LA MANCHE LOWBID")
        print("=" * 55)
        self.abr.afficher_etat()  # Affichage de l'ABR (parcours infixe)
        print(f"  Mises totales : {self.abr.nb_total_mises()}")
        print(f"  Recette vendeur : {self.calculer_recette_vendeur():.2f} euros")
        print(f"  Cout moyen / joueur : {self.calculer_cout_moyen_par_joueur():.2f} euros")
        print(f"  Hauteur ABR : {self.abr.hauteur()}")
        gagnant = self.trouver_gagnant()
        print("-" * 55)
        if gagnant:
            print(f"  GAGNANT : {gagnant[1]} avec le prix {gagnant[0]}")
        else:
            print("  Aucun gagnant - Manche annulee")
        print("=" * 55 + "\n")

    def reinitialiser(self):
        """Remet la manche à zero : ABR vide + liste des mises vide."""
        self.abr   = ABR()  # Nouvel ABR vide
        self.mises = []     # Liste des mises réinitialisée
