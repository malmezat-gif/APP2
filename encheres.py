from abr import ABR
from outils import cout_mise


class Enchere:
    """
    Une enchere correspond a une seule manche.

    On garde :
    - un ABR pour les recherches sur les prix
    - une liste simple des mises pour les calculs de cout
    """

    def __init__(self, cout_base=1.0, alpha=10.0):
        self.abr = ABR()
        self.cout_base = cout_base
        self.alpha = alpha
        self.mises = []

    def ajouter_mise(self, joueur, prix):
        """
        Ajoute une mise.

        On verifie le prix puis on l'enregistre
        dans la liste et dans l'ABR.
        """
        if prix < 0:
            raise ValueError("Le prix doit etre superieur ou egal a 0.")

        if (joueur, prix) in self.mises:
            return

        self.mises.append((joueur, prix))
        self.abr.inserer(prix, joueur)

    def supprimer_mise(self, joueur, prix):
        """
        Supprime une mise precise.

        La suppression est faite :
        - dans la liste des mises
        - puis dans l'ABR
        """
        for index, (nom_joueur, prix_joue) in enumerate(self.mises):
            if nom_joueur == joueur and prix_joue == prix:
                del self.mises[index]
                return self.abr.supprimer_joueur(prix, joueur)
        return False

    def charger_depuis_liste(self, liste_mises):
        """
        Charge une liste de tuples.

        On accepte :
        - (joueur, prix)
        - (manche, joueur, prix)
        """
        for mise in liste_mises:
            if len(mise) == 2:
                joueur, prix = mise
            elif len(mise) == 3:
                _, joueur, prix = mise
            else:
                raise ValueError("Format de mise non reconnu.")

            self.ajouter_mise(joueur, int(prix))

    def trouver_gagnant(self):
        """
        Retourne le plus bas prix unique.

        Le resultat est :
        - None si personne ne gagne
        - (prix, joueur) sinon
        """
        noeud = self.abr.trouver_plus_bas_unique()

        if noeud is None:
            return None

        return noeud.prix, noeud.joueurs[0]

    def calculer_cout_joueur(self, joueur):
        """
        Additionne le cout de toutes les mises d'un joueur.
        """
        total = 0.0

        for nom_joueur, prix in self.mises:
            if nom_joueur == joueur:
                total += cout_mise(prix, self.cout_base, self.alpha)

        return round(total, 2)

    def calculer_recette_vendeur(self):
        """
        Additionne le cout de toutes les mises de la manche.
        """
        total = 0.0

        for _, prix in self.mises:
            total += cout_mise(prix, self.cout_base, self.alpha)

        return round(total, 2)

    def calculer_cout_moyen_par_joueur(self):
        """
        Fait la moyenne des couts par joueur.
        """
        if not self.mises:
            return 0.0

        joueurs = {joueur for joueur, _ in self.mises}
        recette = self.calculer_recette_vendeur()
        return round(recette / len(joueurs), 2)

    def distribution_des_prix(self):
        """Renvoie la repartition des prix dans l'ordre croissant."""
        return self.abr.distribution_prix()

    def resume_enchere(self):
        """
        Construit un texte simple pour afficher l'etat de la manche.
        """
        if self.abr.est_vide():
            return "Aucune mise enregistree.\n"

        lignes = []
        lignes.append("Etat de l'enchere")
        lignes.append("----------------")

        for noeud in self.abr.parcours_infixe():
            joueurs = ", ".join(noeud.joueurs)
            texte = f"Prix {noeud.prix} : {joueurs}"
            if len(noeud.joueurs) == 1:
                texte += " (unique)"
            lignes.append(texte)

        lignes.append("")
        lignes.append(f"Nombre total de mises : {self.abr.nb_total_mises()}")
        lignes.append(f"Recette du vendeur : {self.calculer_recette_vendeur():.2f} euros")
        lignes.append(
            f"Cout moyen par joueur : {self.calculer_cout_moyen_par_joueur():.2f} euros"
        )
        lignes.append(f"Hauteur de l'ABR : {self.abr.hauteur()}")

        gagnant = self.trouver_gagnant()
        if gagnant is None:
            lignes.append("Gagnant : aucun, car il n'y a pas de prix unique.")
        else:
            prix, joueur = gagnant
            lignes.append(f"Gagnant : {joueur} avec le prix {prix}.")

        return "\n".join(lignes) + "\n"

    def resume_distribution(self):
        """
        Construit un texte qui montre combien de joueurs ont choisi chaque prix.
        """
        if self.abr.est_vide():
            return "Aucune donnee chargee.\n"

        lignes = []
        lignes.append("Distribution des prix")
        lignes.append("---------------------")

        for prix, nombre in self.distribution_des_prix().items():
            barre = "#" * nombre
            lignes.append(f"{prix:>3} : {nombre} joueur(s) {barre}")

        return "\n".join(lignes) + "\n"

    def resume_couts(self):
        """
        Construit un texte avec le cout paye par chaque joueur.
        """
        if not self.mises:
            return "Aucune donnee chargee.\n"

        lignes = []
        lignes.append("Couts par joueur")
        lignes.append("----------------")

        joueurs = sorted({joueur for joueur, _ in self.mises})
        for joueur in joueurs:
            cout = self.calculer_cout_joueur(joueur)
            lignes.append(f"{joueur} : {cout:.2f} euros")

        lignes.append(f"Total vendeur : {self.calculer_recette_vendeur():.2f} euros")
        return "\n".join(lignes) + "\n"

    def resume_succ_pred(self):
        """
        Construit un texte avec le predecesseur et le successeur de chaque prix.
        """
        if self.abr.est_vide():
            return "Aucune donnee chargee.\n"

        lignes = []
        lignes.append("Predecesseur et successeur")
        lignes.append("--------------------------")

        for noeud in self.abr.parcours_infixe():
            pred = self.abr.predecesseur(noeud.prix)
            succ = self.abr.successeur(noeud.prix)

            prix_pred = pred.prix if pred else "-"
            prix_succ = succ.prix if succ else "-"
            lignes.append(
                f"Prix {noeud.prix} -> predecesseur : {prix_pred} | successeur : {prix_succ}"
            )

        return "\n".join(lignes) + "\n"

    def reinitialiser(self):
        """Vide completement la manche en cours."""
        self.abr = ABR()
        self.mises = []
