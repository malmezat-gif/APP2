import math
import random
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from encheres import Enchere
from outils import ALPHA, COUT_BASE, NB_MANCHES_SIMULATION, charger_csv, generer_mises_aleatoires
from simulation import simuler_plusieurs_manches, texte_stats_simulation
from strategies import (
    strategie_adaptative,
    strategie_agressive,
    strategie_aleatoire,
    strategie_conservative,
)


class ApplicationLowBid(tk.Tk):
    """
    Fenetre principale du projet.

    L'interface reste simple :
    - a gauche les parametres
    - a droite les onglets de travail
    """

    def __init__(self):
        super().__init__()

        self.title("LowBid - Qui perd gagne !")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.enchere = Enchere(cout_base=COUT_BASE, alpha=ALPHA)

        self.var_cout_base = tk.DoubleVar(value=COUT_BASE)
        self.var_alpha = tk.DoubleVar(value=ALPHA)
        self.var_nb_joueurs = tk.IntVar(value=20)
        self.var_prix_max = tk.IntVar(value=50)
        self.var_nb_manches = tk.IntVar(value=NB_MANCHES_SIMULATION)

        self.var_strat_alea = tk.BooleanVar(value=True)
        self.var_strat_cons = tk.BooleanVar(value=True)
        self.var_strat_agr = tk.BooleanVar(value=True)
        self.var_strat_adapt = tk.BooleanVar(value=False)

        self._construire_interface()

    def _construire_interface(self):
        """
        Monte toute la fenetre.

        On fait une grille a deux colonnes :
        - la colonne de gauche pour les entrees
        - la colonne de droite pour les resultats
        """
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.frame_gauche = ttk.Frame(self, padding=10)
        self.frame_gauche.grid(row=0, column=0, sticky="ns")

        self.frame_droite = ttk.Frame(self, padding=10)
        self.frame_droite.grid(row=0, column=1, sticky="nsew")
        self.frame_droite.columnconfigure(0, weight=1)
        self.frame_droite.rowconfigure(0, weight=1)

        self._construire_panneau_gauche()
        self._construire_onglets()

    def _construire_panneau_gauche(self):
        """
        Cree les champs de parametres et les boutons de base.
        """
        cadre = ttk.LabelFrame(self.frame_gauche, text="Parametres", padding=10)
        cadre.grid(row=0, column=0, sticky="nsew")

        self._ajouter_entree(cadre, "Cout de base", self.var_cout_base, 0)
        self._ajouter_entree(cadre, "Alpha", self.var_alpha, 1)
        self._ajouter_entree(cadre, "Nombre de joueurs", self.var_nb_joueurs, 2)
        self._ajouter_entree(cadre, "Prix max", self.var_prix_max, 3)
        self._ajouter_entree(cadre, "Nombre de manches", self.var_nb_manches, 4)

        ttk.Button(cadre, text="Generer des mises", command=self._generer_mises).grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(10, 5),
        )
        ttk.Button(cadre, text="Charger un CSV", command=self._charger_csv).grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=5,
        )
        ttk.Button(cadre, text="Reinitialiser", command=self._reinitialiser).grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=5,
        )

    def _ajouter_entree(self, parent, texte, variable, ligne):
        """
        Ajoute un label et un champ sur une ligne.
        """
        ttk.Label(parent, text=texte).grid(row=ligne, column=0, sticky="w", pady=4)
        ttk.Entry(parent, textvariable=variable, width=12).grid(
            row=ligne,
            column=1,
            sticky="ew",
            pady=4,
            padx=(8, 0),
        )

    def _construire_onglets(self):
        """
        Cree les 4 onglets du projet.
        """
        self.onglets = ttk.Notebook(self.frame_droite)
        self.onglets.grid(row=0, column=0, sticky="nsew")

        self.tab_enchere = ttk.Frame(self.onglets, padding=10)
        self.tab_simulation = ttk.Frame(self.onglets, padding=10)
        self.tab_analyse = ttk.Frame(self.onglets, padding=10)
        self.tab_humain = ttk.Frame(self.onglets, padding=10)

        self.onglets.add(self.tab_enchere, text="Enchere")
        self.onglets.add(self.tab_simulation, text="Simulation")
        self.onglets.add(self.tab_analyse, text="Analyse")
        self.onglets.add(self.tab_humain, text="Humain vs IA")

        self._construire_onglet_enchere()
        self._construire_onglet_simulation()
        self._construire_onglet_analyse()
        self._construire_onglet_humain()

    def _construire_onglet_enchere(self):
        """
        Cree l'onglet de la manche simple.
        """
        self.tab_enchere.columnconfigure(0, weight=1)
        self.tab_enchere.rowconfigure(1, weight=1)

        barre = ttk.Frame(self.tab_enchere)
        barre.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        ttk.Button(barre, text="Afficher l'enchere", command=self._lancer_enchere).pack(
            side="left",
            padx=(0, 5),
        )
        ttk.Button(barre, text="Infos ABR", command=self._infos_abr).pack(side="left")

        self.texte_enchere = self._creer_zone_texte(
            self.tab_enchere,
            "Charge des donnees puis clique sur 'Afficher l'enchere'.\n",
        )
        self.texte_enchere.grid(row=1, column=0, sticky="nsew")

    def _construire_onglet_simulation(self):
        """
        Cree l'onglet pour comparer les strategies.
        """
        self.tab_simulation.columnconfigure(0, weight=1)
        self.tab_simulation.rowconfigure(2, weight=1)

        cadre = ttk.LabelFrame(self.tab_simulation, text="Strategies", padding=10)
        cadre.grid(row=0, column=0, sticky="ew")

        ttk.Checkbutton(cadre, text="Aleatoire", variable=self.var_strat_alea).pack(side="left", padx=5)
        ttk.Checkbutton(cadre, text="Conservative", variable=self.var_strat_cons).pack(side="left", padx=5)
        ttk.Checkbutton(cadre, text="Agressive", variable=self.var_strat_agr).pack(side="left", padx=5)
        ttk.Checkbutton(cadre, text="Adaptative", variable=self.var_strat_adapt).pack(side="left", padx=5)

        ttk.Button(
            self.tab_simulation,
            text="Lancer la simulation",
            command=self._lancer_simulation,
        ).grid(row=1, column=0, sticky="w", pady=8)

        self.texte_simulation = self._creer_zone_texte(
            self.tab_simulation,
            "Choisis au moins deux strategies si tu veux faire une vraie comparaison.\n",
        )
        self.texte_simulation.grid(row=2, column=0, sticky="nsew")

    def _construire_onglet_analyse(self):
        """
        Cree l'onglet d'analyse de la manche chargee.
        """
        self.tab_analyse.columnconfigure(0, weight=1)
        self.tab_analyse.rowconfigure(1, weight=1)

        barre = ttk.Frame(self.tab_analyse)
        barre.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        ttk.Button(barre, text="Distribution", command=self._afficher_distribution).pack(
            side="left",
            padx=(0, 5),
        )
        ttk.Button(barre, text="Couts", command=self._afficher_couts).pack(side="left", padx=5)
        ttk.Button(barre, text="Successeur / predecesseur", command=self._afficher_succ_pred).pack(
            side="left",
            padx=5,
        )

        self.texte_analyse = self._creer_zone_texte(
            self.tab_analyse,
            "Les analyses utilisent la manche actuellement chargee.\n",
        )
        self.texte_analyse.grid(row=1, column=0, sticky="nsew")

    def _construire_onglet_humain(self):
        """
        Cree l'onglet pour jouer contre l'ordinateur.
        """
        self.tab_humain.columnconfigure(0, weight=1)
        self.tab_humain.rowconfigure(2, weight=1)

        cadre = ttk.LabelFrame(self.tab_humain, text="Votre tour", padding=10)
        cadre.grid(row=0, column=0, sticky="ew")
        cadre.columnconfigure(1, weight=1)

        ttk.Label(cadre, text="Nom").grid(row=0, column=0, sticky="w", pady=4)
        self.entry_nom = ttk.Entry(cadre)
        self.entry_nom.grid(row=0, column=1, sticky="ew", pady=4, padx=(8, 0))

        ttk.Label(cadre, text="Prix").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_prix = ttk.Entry(cadre)
        self.entry_prix.grid(row=1, column=1, sticky="ew", pady=4, padx=(8, 0))

        ttk.Label(cadre, text="Strategie des IA").grid(row=2, column=0, sticky="w", pady=4)
        self.combo_ia = ttk.Combobox(
            cadre,
            values=["Mixte", "Aleatoire", "Conservative", "Agressive"],
            state="readonly",
        )
        self.combo_ia.grid(row=2, column=1, sticky="ew", pady=4, padx=(8, 0))
        self.combo_ia.set("Mixte")

        ttk.Button(self.tab_humain, text="Jouer la manche", command=self._jouer_humain).grid(
            row=1,
            column=0,
            sticky="w",
            pady=8,
        )

        self.texte_humain = self._creer_zone_texte(
            self.tab_humain,
            "Entre ton nom et ton prix pour lancer une manche contre les IA.\n",
        )
        self.texte_humain.grid(row=2, column=0, sticky="nsew")

    def _creer_zone_texte(self, parent, message_depart):
        """
        Cree une zone de texte avec barre de defilement integree.
        """
        zone = scrolledtext.ScrolledText(parent, wrap="word", font=("Courier", 11))
        zone.insert("end", message_depart)
        return zone

    def _lire_parametres(self):
        """
        Lit et verifie tous les parametres numeriques.
        """
        try:
            cout_base = float(self.var_cout_base.get())
            alpha = float(self.var_alpha.get())
            nb_joueurs = int(self.var_nb_joueurs.get())
            prix_max = int(self.var_prix_max.get())
            nb_manches = int(self.var_nb_manches.get())
        except tk.TclError as erreur:
            raise ValueError("Un parametre n'est pas valide.") from erreur

        if cout_base < 0 or alpha < 0:
            raise ValueError("Le cout de base et alpha doivent etre positifs.")
        if nb_joueurs <= 0 or nb_manches <= 0:
            raise ValueError("Le nombre de joueurs et de manches doit etre > 0.")
        if prix_max < 0:
            raise ValueError("Le prix max doit etre >= 0.")

        return cout_base, alpha, nb_joueurs, prix_max, nb_manches

    def _lire_cout_alpha(self):
        """
        Lit seulement le cout de base et alpha.
        """
        try:
            cout_base = float(self.var_cout_base.get())
            alpha = float(self.var_alpha.get())
        except tk.TclError as erreur:
            raise ValueError("Le cout de base ou alpha n'est pas valide.") from erreur

        if cout_base < 0 or alpha < 0:
            raise ValueError("Le cout de base et alpha doivent etre positifs.")

        return cout_base, alpha

    def _nouvelle_enchere(self):
        """
        Recree une enchere avec les parametres du moment.
        """
        cout_base, alpha = self._lire_cout_alpha()
        self.enchere = Enchere(cout_base=cout_base, alpha=alpha)

    def _generer_mises(self):
        """
        Genere des mises au hasard et les charge dans l'enchere.
        """
        try:
            _, _, nb_joueurs, prix_max, _ = self._lire_parametres()
            self._nouvelle_enchere()
            mises = generer_mises_aleatoires(nb_joueurs, prix_max)
            self.enchere.charger_depuis_liste(mises)
            self._ecrire(self.texte_enchere, f"{len(mises)} mises aleatoires ont ete generees.\n")
        except Exception as erreur:
            messagebox.showerror("Erreur", str(erreur))

    def _charger_csv(self):
        """
        Ouvre un fichier CSV puis charge les mises dans l'enchere.
        """
        chemin = filedialog.askopenfilename(
            title="Choisir un fichier CSV",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")],
        )

        if not chemin:
            return

        try:
            self._nouvelle_enchere()
            mises = charger_csv(chemin)
            self.enchere.charger_depuis_liste(mises)
            self._ecrire(self.texte_enchere, f"{len(mises)} mises chargees depuis {chemin}.\n")
        except Exception as erreur:
            messagebox.showerror("Erreur", str(erreur))

    def _reinitialiser(self):
        """
        Vide la manche en cours.
        """
        self.enchere.reinitialiser()
        self._ecrire(self.texte_enchere, "Enchere reinitialisee.\n")

    def _lancer_enchere(self):
        """
        Affiche le resume de la manche actuelle.
        """
        self._ecrire(self.texte_enchere, "\n" + self.enchere.resume_enchere())

    def _infos_abr(self):
        """
        Donne quelques infos simples sur la forme de l'ABR.
        """
        if self.enchere.abr.est_vide():
            self._ecrire(self.texte_enchere, "Aucune mise chargee.\n")
            return

        nombre_mises = self.enchere.abr.nb_total_mises()
        hauteur = self.enchere.abr.hauteur()
        hauteur_theorique = math.log2(nombre_mises + 1) if nombre_mises > 0 else 0

        lignes = []
        lignes.append("Infos sur l'ABR")
        lignes.append("----------------")
        lignes.append(f"Nombre de mises : {nombre_mises}")
        lignes.append(f"Hauteur actuelle : {hauteur}")
        lignes.append(f"Hauteur theorique environ : {hauteur_theorique:.2f}")

        if nombre_mises > 5 and hauteur > 3 * hauteur_theorique:
            lignes.append("L'arbre semble trop haut. Il commence a se degenerer.")
        else:
            lignes.append("La forme de l'arbre reste correcte pour cette manche.")

        self._ecrire(self.texte_enchere, "\n" + "\n".join(lignes) + "\n")

    def _strategies_choisies(self):
        """
        Recupere les strategies cochees dans l'onglet simulation.
        """
        strategies = {}

        if self.var_strat_alea.get():
            strategies["aleatoire"] = strategie_aleatoire
        if self.var_strat_cons.get():
            strategies["conservative"] = strategie_conservative
        if self.var_strat_agr.get():
            strategies["agressive"] = strategie_agressive
        if self.var_strat_adapt.get():
            strategies["adaptative"] = strategie_adaptative

        return strategies

    def _lancer_simulation(self):
        """
        Lance la simulation dans un thread pour ne pas bloquer la fenetre.
        """
        try:
            cout_base, alpha, nb_joueurs, prix_max, nb_manches = self._lire_parametres()
        except Exception as erreur:
            messagebox.showerror("Erreur", str(erreur))
            return

        strategies = self._strategies_choisies()
        if not strategies:
            self._ecrire(self.texte_simulation, "Coche au moins une strategie.\n")
            return

        self._ecrire(self.texte_simulation, f"Simulation en cours sur {nb_manches} manches...\n")

        def travail():
            try:
                stats = simuler_plusieurs_manches(
                    strategies,
                    nb_joueurs=nb_joueurs,
                    nb_manches=nb_manches,
                    cout_base=cout_base,
                    alpha=alpha,
                    prix_max=prix_max,
                )
                texte = texte_stats_simulation(stats, nb_manches)
                self.after(0, lambda: self._ecrire(self.texte_simulation, "\n" + texte))
            except Exception as erreur:
                self.after(0, lambda: messagebox.showerror("Erreur", str(erreur)))

        thread = threading.Thread(target=travail, daemon=True)
        thread.start()

    def _afficher_distribution(self):
        """
        Affiche la repartition des prix de la manche actuelle.
        """
        self._ecrire(self.texte_analyse, "\n" + self.enchere.resume_distribution())

    def _afficher_couts(self):
        """
        Affiche les couts par joueur.
        """
        self._ecrire(self.texte_analyse, "\n" + self.enchere.resume_couts())

    def _afficher_succ_pred(self):
        """
        Affiche le predecesseur et le successeur de chaque prix.
        """
        self._ecrire(self.texte_analyse, "\n" + self.enchere.resume_succ_pred())

    def _jouer_humain(self):
        """
        Lance une manche avec un humain et des IA.

        On lit les champs, on joue la manche puis on affiche le resultat.
        """
        try:
            cout_base, alpha, nb_joueurs, prix_max, _ = self._lire_parametres()
        except Exception as erreur:
            messagebox.showerror("Erreur", str(erreur))
            return

        nom = self.entry_nom.get().strip()
        if not nom:
            self._ecrire(self.texte_humain, "Entre un nom avant de jouer.\n")
            return

        try:
            prix_humain = int(self.entry_prix.get())
        except ValueError:
            self._ecrire(self.texte_humain, "Le prix doit etre un entier.\n")
            return

        if prix_humain < 0 or prix_humain > prix_max:
            self._ecrire(self.texte_humain, f"Le prix doit etre entre 0 et {prix_max}.\n")
            return

        manche = Enchere(cout_base=cout_base, alpha=alpha)
        manche.ajouter_mise(nom, prix_humain)

        mode_ia = self.combo_ia.get()
        strategies_mixte = [
            strategie_aleatoire,
            strategie_conservative,
            strategie_agressive,
        ]

        for numero in range(1, nb_joueurs + 1):
            nom_ia = f"IA_{numero:02d}"

            if mode_ia == "Aleatoire":
                prix_ia = strategie_aleatoire(prix_max)
            elif mode_ia == "Conservative":
                prix_ia = strategie_conservative(prix_max)
            elif mode_ia == "Agressive":
                prix_ia = strategie_agressive(prix_max)
            else:
                strategie = random.choice(strategies_mixte)
                prix_ia = strategie(prix_max)

            manche.ajouter_mise(nom_ia, prix_ia)

        gagnant = manche.trouver_gagnant()
        noeud_humain = manche.abr.rechercher(prix_humain)

        lignes = []
        lignes.append(f"Manche de {nom} contre {nb_joueurs} IA")
        lignes.append("--------------------------------")
        lignes.append(f"Votre prix : {prix_humain}")
        lignes.append(f"Votre cout : {manche.calculer_cout_joueur(nom):.2f} euros")
        lignes.append(f"Recette du vendeur : {manche.calculer_recette_vendeur():.2f} euros")

        if gagnant is None:
            lignes.append("Aucun gagnant cette fois.")
        else:
            prix_gagnant, joueur_gagnant = gagnant
            lignes.append(f"Gagnant : {joueur_gagnant} avec le prix {prix_gagnant}")

            if joueur_gagnant == nom:
                lignes.append("Bravo, votre prix etait le plus bas prix unique.")
            elif noeud_humain and len(noeud_humain.joueurs) > 1:
                lignes.append(
                    f"Votre prix n'etait pas unique : {len(noeud_humain.joueurs)} joueurs l'ont choisi."
                )
            else:
                lignes.append("Votre prix etait unique, mais un plus petit prix unique a gagne.")

        self._ecrire(self.texte_humain, "\n" + "\n".join(lignes) + "\n")

    def _ecrire(self, zone, texte):
        """
        Ajoute du texte a la fin d'une zone puis descend tout en bas.
        """
        zone.insert("end", texte)
        zone.see("end")


if __name__ == "__main__":
    application = ApplicationLowBid()
    application.mainloop()
