# ============================================================
# interface.py - Interface graphique LowBid (CustomTkinter)
# Fenêtre principale de la plateforme d'enchères inversées.
# Contient 4 onglets : Enchère, Simulation, Analyse, Humain vs IA
# ============================================================

import customtkinter as ctk    # Bibliothèque pour l'interface graphique moderne (à installer : pip install customtkinter)
import tkinter as tk           # Module Tkinter de base pour certains widgets natifs (filedialog, etc.)
import threading               # Module pour exécuter la simulation en arrière-plan (sans bloquer l'interface)
import random                  # Module pour les choix aléatoires dans le mode Humain vs IA

from encheres  import Enchere                  # Moteur d'une manche d'enchère
from abr       import ABR                      # Arbre Binaire de Recherche
from outils    import (
    cout_mise,                                 # Calcul du coût d'une mise
    charger_csv,                               # Chargement d'un fichier CSV
    generer_mises_aleatoires,                  # Génération aléatoire de mises
    COUT_BASE, ALPHA,                          # Paramètres par défaut
    NB_MANCHES_SIMULATION                      # Nombre de manches par défaut pour la simulation
)
from strategies import (
    strategie_aleatoire,                       # Stratégie : prix aléatoire
    strategie_conservative,                    # Stratégie : prix élevés
    strategie_agressive,                       # Stratégie : petits prix
    strategie_adaptative                       # Stratégie : évite les prix populaires
)
from simulation import simuler_plusieurs_manches  # Simulation multi-manches

# --- Configuration du thème de l'interface graphique ---
ctk.set_appearance_mode("dark")       # Thème sombre (options : "dark", "light", "system")
ctk.set_default_color_theme("blue")   # Couleur principale : bleu (options : "blue", "green", "dark-blue")


class ApplicationLowBid(ctk.CTk):
    """
    Fenêtre principale de l'application LowBid "Qui perd gagne !".
    Hérite de CTk (CustomTkinter) qui est lui-même basé sur Tkinter.
    """

    def __init__(self):
        """
        Constructeur : initialise la fenêtre et tous ses composants internes.
        """
        super().__init__()  # Appel obligatoire du constructeur de la classe parente (CTk)

        # --- Configuration générale de la fenêtre ---
        self.title("LowBid — Qui perd gagne !")   # Titre affiché dans la barre de la fenêtre
        self.geometry("1150x720")                  # Dimensions initiales : largeur x hauteur (en pixels)
        self.resizable(True, True)                 # L'utilisateur peut redimensionner la fenêtre

        # --- État interne de l'application ---
        self.enchere = Enchere(cout_base=COUT_BASE, alpha=ALPHA)  # Manche courante
        self.historique_manches = []   # Historique de toutes les manches jouées (pour l'analyse)

        # --- Variables liées aux curseurs et champs de paramètres ---
        self.var_cout_base  = ctk.DoubleVar(value=COUT_BASE)          # Valeur du coût de base
        self.var_alpha      = ctk.DoubleVar(value=ALPHA)              # Valeur de alpha
        self.var_nb_joueurs = ctk.IntVar(value=20)                    # Nombre de joueurs IA
        self.var_prix_max   = ctk.IntVar(value=50)                    # Prix maximum possible
        self.var_nb_manches = ctk.IntVar(value=NB_MANCHES_SIMULATION) # Nb manches pour la simulation

        # --- Construction de l'interface graphique ---
        self._construire_interface()  # Appel de la méthode qui crée tous les widgets

    # ==========================================================
    # CONSTRUCTION DE L'INTERFACE
    # ==========================================================

    def _construire_interface(self):
        """
        Construit et organise tous les éléments de l'interface en deux zones :
        - Colonne gauche : panneau de contrôle et paramètres
        - Colonne droite : zone principale avec 4 onglets
        """
        # Configuration du système de grille : 2 colonnes, la droite est extensible
        self.grid_columnconfigure(1, weight=1)  # La colonne 1 (droite) s'étire avec la fenêtre
        self.grid_rowconfigure(0, weight=1)     # La ligne 0 s'étire verticalement

        # ── PANNEAU GAUCHE (contrôles et paramètres) ──────────────
        self.frame_gauche = ctk.CTkFrame(self, width=290)  # Cadre de largeur fixe
        self.frame_gauche.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_gauche.grid_propagate(False)  # Empêche le cadre de réduire sa largeur

        self._construire_panneau_gauche()  # Remplit le panneau gauche avec ses widgets

        # ── ZONE PRINCIPALE (système d'onglets) ───────────────────
        self.onglets = ctk.CTkTabview(self)  # Widget d'onglets (CTkTabview)
        self.onglets.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Ajout des 4 onglets principaux
        self.onglets.add("Enchère")       # Onglet pour visualiser et lancer une manche
        self.onglets.add("Simulation")    # Onglet pour la simulation multi-manches
        self.onglets.add("Analyse")       # Onglet pour l'analyse des données
        self.onglets.add("Humain vs IA")  # Onglet pour jouer contre l'IA

        # Construction du contenu de chaque onglet
        self._construire_onglet_enchere()
        self._construire_onglet_simulation()
        self._construire_onglet_analyse()
        self._construire_onglet_humain()

    def _construire_panneau_gauche(self):
        """
        Crée le panneau de contrôle gauche avec :
        - Les curseurs pour les paramètres (cout_base, alpha, nb_joueurs, prix_max)
        - Les boutons de chargement de données
        """
        # Titre du panneau
        ctk.CTkLabel(
            self.frame_gauche,
            text="PARAMETRES",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(18, 5))  # Espacement vertical autour du label

        ctk.CTkSeparator(self.frame_gauche).pack(fill="x", padx=15, pady=5)  # Ligne de séparation

        # ── Curseur : Coût de base ──
        ctk.CTkLabel(self.frame_gauche, text="Cout de base (euros)").pack(pady=(12, 2))
        ctk.CTkSlider(
            self.frame_gauche,
            from_=0.5, to=5.0,              # Plage de valeurs possibles
            variable=self.var_cout_base,    # Variable Python liée au curseur
            number_of_steps=18,             # Nombre de positions discrètes du curseur
            command=self._maj_labels        # Fonction appelée à chaque déplacement du curseur
        ).pack(padx=20, fill="x")
        self.label_cout_base = ctk.CTkLabel(self.frame_gauche, text=f"{COUT_BASE:.2f} euros")
        self.label_cout_base.pack()  # Label qui affiche la valeur courante du curseur

        # ── Curseur : Alpha (prime de risque) ──
        ctk.CTkLabel(self.frame_gauche, text="Alpha (prime de risque)").pack(pady=(12, 2))
        ctk.CTkSlider(
            self.frame_gauche,
            from_=0, to=50,
            variable=self.var_alpha,
            number_of_steps=50,
            command=self._maj_labels
        ).pack(padx=20, fill="x")
        self.label_alpha = ctk.CTkLabel(self.frame_gauche, text=f"alpha = {ALPHA}")
        self.label_alpha.pack()

        # ── Curseur : Nombre de joueurs IA ──
        ctk.CTkLabel(self.frame_gauche, text="Nombre de joueurs IA").pack(pady=(12, 2))
        ctk.CTkSlider(
            self.frame_gauche,
            from_=5, to=100,
            variable=self.var_nb_joueurs,
            number_of_steps=95,
            command=self._maj_labels
        ).pack(padx=20, fill="x")
        self.label_nb_joueurs = ctk.CTkLabel(self.frame_gauche, text="20 joueurs")
        self.label_nb_joueurs.pack()

        # ── Curseur : Prix maximum ──
        ctk.CTkLabel(self.frame_gauche, text="Prix maximum").pack(pady=(12, 2))
        ctk.CTkSlider(
            self.frame_gauche,
            from_=10, to=200,
            variable=self.var_prix_max,
            number_of_steps=190,
            command=self._maj_labels
        ).pack(padx=20, fill="x")
        self.label_prix_max = ctk.CTkLabel(self.frame_gauche, text="Prix max : 50")
        self.label_prix_max.pack()

        ctk.CTkSeparator(self.frame_gauche).pack(fill="x", padx=15, pady=15)

        # ── Section : Données ──
        ctk.CTkLabel(
            self.frame_gauche,
            text="Données",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(0, 8))

        # Bouton : générer des mises aléatoires
        ctk.CTkButton(
            self.frame_gauche,
            text="Generer aleatoirement",
            command=self._generer_mises   # Appelle la méthode de génération aléatoire
        ).pack(padx=20, pady=4, fill="x")

        # Bouton : charger depuis un fichier CSV
        ctk.CTkButton(
            self.frame_gauche,
            text="Charger un CSV",
            command=self._charger_csv,    # Ouvre une boîte de dialogue pour sélectionner un CSV
            fg_color="gray"               # Couleur différente pour distinguer l'action
        ).pack(padx=20, pady=4, fill="x")

        # Bouton : réinitialiser l'enchère (rouge pour signaler une action irréversible)
        ctk.CTkButton(
            self.frame_gauche,
            text="Reinitialiser",
            command=self._reinitialiser,
            fg_color="#c0392b"            # Rouge = danger / action destructive
        ).pack(padx=20, pady=(4, 20), fill="x")

    def _construire_onglet_enchere(self):
        """
        Construit le contenu de l'onglet "Enchère" :
        - Barre de contrôle avec boutons d'action
        - Zone de texte scrollable pour afficher les résultats
        """
        frame = self.onglets.tab("Enchère")  # Récupération du cadre de l'onglet
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)   # La zone de texte occupe tout l'espace disponible

        # Barre de contrôle en haut de l'onglet
        frame_ctrl = ctk.CTkFrame(frame)
        frame_ctrl.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(
            frame_ctrl,
            text="Lancer l'enchere",
            command=self._lancer_enchere,       # Lance l'enchère et affiche les résultats
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=10, pady=8)

        ctk.CTkButton(
            frame_ctrl,
            text="Infos sur l'ABR",
            command=self._infos_abr             # Affiche les informations structurelles de l'ABR
        ).pack(side="left", padx=5, pady=8)

        # Zone de texte scrollable pour afficher les résultats (police à espacement fixe pour l'alignement)
        self.texte_enchere = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(family="Courier", size=12)
        )
        self.texte_enchere.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.texte_enchere.insert("end", "Bienvenue dans LowBid !\n\n")
        self.texte_enchere.insert("end", "Utilisez le panneau gauche pour charger ou generer des mises,\n")
        self.texte_enchere.insert("end", "puis cliquez sur 'Lancer l'enchere' pour voir les resultats.\n")

    def _construire_onglet_simulation(self):
        """
        Construit l'onglet "Simulation" :
        - Sélection des stratégies à comparer (cases à cocher)
        - Nombre de manches
        - Bouton de lancement + zone de résultats
        """
        frame = self.onglets.tab("Simulation")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(4, weight=1)   # La zone de texte s'étire

        ctk.CTkLabel(
            frame,
            text="Simulation multi-manches",
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, pady=10)

        # Cadre pour la sélection des stratégies
        frame_strat = ctk.CTkFrame(frame)
        frame_strat.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(frame_strat, text="Strategies :").pack(side="left", padx=10)

        # Variables booléennes liées aux cases à cocher (True = stratégie activée)
        self.var_strat_alea  = ctk.BooleanVar(value=True)   # Aléatoire activée par défaut
        self.var_strat_cons  = ctk.BooleanVar(value=True)   # Conservative activée par défaut
        self.var_strat_agr   = ctk.BooleanVar(value=True)   # Agressive activée par défaut
        self.var_strat_adapt = ctk.BooleanVar(value=False)  # Adaptative désactivée par défaut

        ctk.CTkCheckBox(frame_strat, text="Aleatoire",    variable=self.var_strat_alea).pack(side="left", padx=5)
        ctk.CTkCheckBox(frame_strat, text="Conservative", variable=self.var_strat_cons).pack(side="left", padx=5)
        ctk.CTkCheckBox(frame_strat, text="Agressive",    variable=self.var_strat_agr).pack(side="left", padx=5)
        ctk.CTkCheckBox(frame_strat, text="Adaptative",   variable=self.var_strat_adapt).pack(side="left", padx=5)

        # Cadre pour le nombre de manches
        frame_nb = ctk.CTkFrame(frame)
        frame_nb.grid(row=2, column=0, padx=10, pady=4, sticky="ew")
        ctk.CTkLabel(frame_nb, text="Nombre de manches :").pack(side="left", padx=10)
        ctk.CTkEntry(frame_nb, textvariable=self.var_nb_manches, width=90).pack(side="left", padx=5)

        # Bouton de lancement de la simulation
        ctk.CTkButton(
            frame,
            text="Lancer la simulation",
            command=self._lancer_simulation,    # Lance la simulation dans un thread séparé
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=3, column=0, pady=8)

        # Zone d'affichage des résultats de simulation
        self.texte_simulation = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(family="Courier", size=12)
        )
        self.texte_simulation.grid(row=4, column=0, padx=5, pady=5, sticky="nsew")
        self.texte_simulation.insert("end", "Selectionnez les strategies et lancez la simulation.\n")

    def _construire_onglet_analyse(self):
        """
        Construit l'onglet "Analyse" :
        - Boutons pour différentes analyses (distribution, coûts, successeurs)
        - Zone de texte pour afficher les résultats
        """
        frame = self.onglets.tab("Analyse")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # Barre de boutons d'analyse
        frame_btn = ctk.CTkFrame(frame)
        frame_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(
            frame_btn, text="Distribution des prix",
            command=self._afficher_distribution   # Répartition des mises par prix
        ).pack(side="left", padx=5, pady=8)

        ctk.CTkButton(
            frame_btn, text="Couts par joueur",
            command=self._afficher_couts          # Coût individuel de chaque joueur
        ).pack(side="left", padx=5, pady=8)

        ctk.CTkButton(
            frame_btn, text="Successeur / Predecesseur",
            command=self._afficher_succ_pred      # Navigation dans l'ABR
        ).pack(side="left", padx=5, pady=8)

        # Zone de texte pour les résultats d'analyse
        self.texte_analyse = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(family="Courier", size=12)
        )
        self.texte_analyse.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.texte_analyse.insert("end", "Chargez des donnees pour commencer l'analyse.\n")

    def _construire_onglet_humain(self):
        """
        Construit l'onglet "Humain vs IA" :
        - Saisie du nom et du prix du joueur humain
        - Choix de la stratégie des adversaires IA
        - Bouton pour soumettre la mise + zone de résultats
        """
        frame = self.onglets.tab("Humain vs IA")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            frame,
            text="Jouez contre l'IA !",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, pady=12)

        # Cadre de configuration du joueur humain
        frame_config = ctk.CTkFrame(frame)
        frame_config.grid(row=1, column=0, padx=30, pady=5, sticky="ew")
        frame_config.grid_columnconfigure(1, weight=1)

        # Champ : nom du joueur humain
        ctk.CTkLabel(frame_config, text="Votre nom :").grid(row=0, column=0, padx=15, pady=8, sticky="w")
        self.entry_nom = ctk.CTkEntry(frame_config, placeholder_text="ex : Thibault")
        self.entry_nom.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        # Champ : prix proposé par le joueur humain
        ctk.CTkLabel(frame_config, text="Votre prix :").grid(row=1, column=0, padx=15, pady=8, sticky="w")
        self.entry_prix = ctk.CTkEntry(frame_config, placeholder_text="Entier entre 0 et prix max")
        self.entry_prix.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        # Menu déroulant : choix de la stratégie des adversaires IA
        ctk.CTkLabel(frame_config, text="Adversaires IA :").grid(row=2, column=0, padx=15, pady=8, sticky="w")
        self.combo_ia = ctk.CTkComboBox(
            frame_config,
            values=["Mixte", "Aleatoire", "Conservative", "Agressive"]  # Options disponibles
        )
        self.combo_ia.grid(row=2, column=1, padx=10, pady=8, sticky="ew")
        self.combo_ia.set("Mixte")  # Sélection par défaut : stratégie mixte (plus réaliste)

        # Bouton de soumission de la mise
        ctk.CTkButton(
            frame,
            text="Soumettre ma mise",
            command=self._jouer_humain,           # Lance une manche avec la mise humaine
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=2, column=0, pady=10)

        # Zone de résultats du mode humain
        self.texte_humain = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(family="Courier", size=12)
        )
        self.texte_humain.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
        self.texte_humain.insert("end", "Entrez votre nom et votre prix, puis soumettez votre mise.\n")

    # ==========================================================
    # MÉTHODES D'ACTION (liées aux boutons)
    # ==========================================================

    def _maj_labels(self, _=None):
        """
        Met à jour l'affichage des labels de valeur des curseurs.
        Appelée automatiquement à chaque déplacement d'un curseur (via 'command=').
        Le paramètre '_' reçoit la valeur du curseur mais on l'ignore (on lit directement les variables).
        """
        self.label_cout_base.configure(text=f"{self.var_cout_base.get():.2f} euros")
        self.label_alpha.configure(text=f"alpha = {self.var_alpha.get():.0f}")
        self.label_nb_joueurs.configure(text=f"{self.var_nb_joueurs.get()} joueurs")
        self.label_prix_max.configure(text=f"Prix max : {self.var_prix_max.get()}")

    def _generer_mises(self):
        """
        Génère des mises aléatoires selon les paramètres actuels et les charge dans l'enchère.
        """
        nb       = self.var_nb_joueurs.get()   # Nombre de joueurs à simuler
        prix_max = self.var_prix_max.get()     # Prix maximum pour la génération

        mises = generer_mises_aleatoires(nb, prix_max)  # Génération d'une liste de (joueur, prix) aléatoires

        self.enchere.reinitialiser()                   # On efface les données de l'enchère précédente
        self.enchere.cout_base = self.var_cout_base.get()  # Mise ã jour du coût de base
        self.enchere.alpha     = self.var_alpha.get()      # Mise à jour d'alpha
        self.enchere.charger_depuis_liste(mises)           # Insertion de toutes les mises dans l'ABR

        self._ecrire_enchere(f"OK : {nb} mises generees aleatoirement (prix max = {prix_max})\n")

    def _charger_csv(self):
        """
        Ouvre une boîte de dialogue de sélection de fichier, charge le CSV choisi.
        """
        from tkinter import filedialog  # Import local pour ouvrir la boîte de dialogue

        # Boîte de dialogue : l'utilisateur choisit un fichier CSV
        chemin = filedialog.askopenfilename(
            title="Selectionner un fichier CSV de mises",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
        )

        if chemin:
            mises = charger_csv(chemin)  # Lecture et conversion du CSV en liste de mises
            if mises:
                self.enchere.reinitialiser()          # Réinitialisation avant chargement
                self.enchere.charger_depuis_liste(mises)  # Insertion dans l'ABR
                self._ecrire_enchere(f"OK : {len(mises)} mises chargees depuis {chemin}\n")
            else:
                self._ecrire_enchere("Erreur : fichier CSV vide ou format invalide.\n")

    def _reinitialiser(self):
        """
        Remet l'enchère complètement à zéro (ABR et liste des mises vidés).
        """
        self.enchere.reinitialiser()      # Réinitialisation de l'objet Enchere
        self.historique_manches = []      # Effacement de l'historique des manches
        self._ecrire_enchere("Enchere reinitialise.\n")

    def _lancer_enchere(self):
        """
        Lance l'enchère avec les données chargées et affiche tous les résultats :
        état de l'ABR (parcours infixe), statistiques, gagnant.
        """
        if self.enchere.abr.est_vide():
            self._ecrire_enchere("Aucune mise chargee. Generez ou importez des donnees d'abord.\n")
            return

        # Construction du texte de résultats manuellement (sans print, on écrit dans le widget)
        t = "\n" + "=" * 55 + "\n"
        t += "  ETAT DE L'ENCHERE (parcours infixe = prix tries)\n"
        t += "=" * 55 + "\n"

        for noeud in self.enchere.abr.parcours_infixe():  # On parcourt les nœuds dans l'ordre croissant
            if len(noeud.joueurs) == 1:
                indicateur = "  UNIQUE"  # Ce prix n'appartient qu'à un joueur
            else:
                indicateur = f"  ({len(noeud.joueurs)} joueurs)"

            t += f"  Prix {noeud.prix:4d}  ->  {noeud.joueurs}  {indicateur}\n"

        t += "=" * 55 + "\n"
        t += f"\n  Mises totales   : {self.enchere.abr.nb_total_mises()}\n"
        t += f"  Recette vendeur : {self.enchere.calculer_recette_vendeur():.2f} euros\n"
        t += f"  Cout moyen      : {self.enchere.calculer_cout_moyen_par_joueur():.2f} euros / joueur\n"
        t += f"  Hauteur ABR     : {self.enchere.abr.hauteur()}\n"

        gagnant = self.enchere.trouver_gagnant()  # On cherche le gagnant dans l'ABR
        t += "\n" + "-" * 55 + "\n"
        if gagnant:
            prix_g, joueur_g = gagnant
            t += f"  GAGNANT : {joueur_g} --- Prix gagnant : {prix_g}\n"
        else:
            t += "  Aucun gagnant --- Manche annulee (aucun prix unique)\n"
        t += "=" * 55 + "\n"

        self._ecrire_enchere(t)

    def _infos_abr(self):
        """
        Affiche des informations structurelles sur l'ABR courant :
        hauteur actuelle vs hauteur idéale, risque de dégénérescence.
        """
        if self.enchere.abr.est_vide():
            self._ecrire_enchere("ABR vide. Chargez des donnees d'abord.\n")
            return

        import math
        n = self.enchere.abr.nb_total_mises()         # Nombre total de mises
        h = self.enchere.abr.hauteur()                 # Hauteur actuelle
        h_ideal = math.log2(n + 1) if n > 0 else 0    # Hauteur théorique d'un ABR parfaitement équilibré

        t  = f"\n  Informations sur l'ABR :\n"
        t += f"  Nombre de mises    : {n}\n"
        t += f"  Hauteur actuelle   : {h}\n"
        t += f"  Hauteur ideale     : {h_ideal:.1f} (= log2({n}+1))\n"

        if h > 3 * h_ideal and n > 5:
            # L'arbre est beaucoup trop haut → il dégénère (insertions en ordre croissant/décroissant)
            t += "  ATTENTION : L'ABR degenerese ! (hauteur >> log2(n))\n"
            t += "  Solution : utiliser un AVL ou un dictionnaire + tri.\n"
        else:
            t += "  L'ABR est en bonne forme structurelle.\n"

        self._ecrire_enchere(t)

    def _lancer_simulation(self):
        """
        Lance la simulation multi-manches dans un thread en arrière-plan.
        Utiliser un thread évite de "geler" l'interface graphique pendant le calcul.
        """
        # Collecte des stratégies cochées par l'utilisateur
        strategies_choisies = {}
        if self.var_strat_alea.get():
            strategies_choisies["aleatoire"]    = strategie_aleatoire
        if self.var_strat_cons.get():
            strategies_choisies["conservative"] = strategie_conservative
        if self.var_strat_agr.get():
            strategies_choisies["agressive"]    = strategie_agressive
        if self.var_strat_adapt.get():
            strategies_choisies["adaptative"]   = strategie_adaptative

        if not strategies_choisies:
            self._ecrire_simulation("Cochez au moins une strategie avant de lancer.\n")
            return

        nb_manches = self.var_nb_manches.get()  # Récupération du nombre de manches souhaité
        self._ecrire_simulation(f"Simulation de {nb_manches} manches en cours...\n")

        def tache_simulation():
            """Fonction exécutée dans le thread séparé."""
            resultats = simuler_plusieurs_manches(
                strategies_equipes=strategies_choisies,
                nb_joueurs=self.var_nb_joueurs.get(),
                nb_manches=nb_manches,
                cout_base=self.var_cout_base.get(),
                alpha=self.var_alpha.get(),
                prix_max=self.var_prix_max.get(),
            )
            # On revient dans le thread principal pour mettre à jour l'interface (sécurité Tkinter)
            self.after(0, lambda: self._afficher_resultats_simulation(resultats, nb_manches))

        # Création et démarrage du thread en arrière-plan (daemon=True : il s'arrête avec l'appli)
        thread = threading.Thread(target=tache_simulation, daemon=True)
        thread.start()

    def _afficher_resultats_simulation(self, stats, nb_manches):
        """
        Affiche les résultats de la simulation dans l'onglet Simulation.
        Appelée depuis le thread principal après la fin du calcul.
        """
        t  = f"\n{'=' * 60}\n"
        t += f"  RESULTATS - {nb_manches} manches simulees\n"
        t += f"{'=' * 60}\n"

        for nom, donnees in stats.items():
            if nom == "vendeur":
                continue  # On affiche le vendeur séparément

            victoires  = donnees["victoires"]
            taux       = victoires / nb_manches * 100
            gain_moyen = donnees["gains_totaux"] / max(victoires, 1)

            t += f"\n  Strategie : {nom.upper()}\n"
            t += f"    Victoires    : {victoires} ({taux:.1f}%)\n"
            t += f"    Prix moyen   : {gain_moyen:.1f}\n"

        recette   = stats["vendeur"]["recette_totale"]
        annulees  = stats["vendeur"]["manches_sans_gagnant"]

        t += f"\n  {'─' * 45}\n"
        t += f"  VENDEUR\n"
        t += f"    Recette totale  : {recette:.2f} euros\n"
        t += f"    Recette/manche  : {recette / nb_manches:.2f} euros\n"
        t += f"    Manches annulees: {annulees} ({annulees / nb_manches * 100:.1f}%)\n"
        t += f"{'=' * 60}\n"

        self._ecrire_simulation(t)

    def _afficher_distribution(self):
        """
        Affiche la distribution des mises par prix dans l'onglet Analyse.
        Montre combien de joueurs ont misé chaque prix, avec une barre visuelle.
        """
        if self.enchere.abr.est_vide():
            self._ecrire_analyse("Chargez des donnees pour afficher la distribution.\n")
            return

        distribution = self.enchere.abr.distribution_prix()  # Dictionnaire {prix: nb joueurs}

        t  = "\n  DISTRIBUTION DES PRIX\n  " + "-" * 45 + "\n"
        t += f"  {'Prix':>6}  {'Joueurs':>8}  Graphique\n"
        t += "  " + "-" * 45 + "\n"

        for prix, nb in distribution.items():
            barre  = "|" * nb          # Barre proportionnelle (1 barre = 1 joueur)
            unique = " UNIQUE" if nb == 1 else ""  # Indicateur si prix unique
            t += f"  {prix:>6}  {nb:>8}  {barre}{unique}\n"

        self._ecrire_analyse(t)

    def _afficher_couts(self):
        """
        Affiche les coûts payés par chaque joueur dans l'onglet Analyse.
        """
        if not self.enchere.mises:
            self._ecrire_analyse("Aucune mise enregistree.\n")
            return

        # Récupération des joueurs uniques présents dans les mises
        joueurs = sorted(set(j for (j, _) in self.enchere.mises))  # Trié alphabétiquement

        t  = "\n  COUTS PAR JOUEUR\n  " + "-" * 38 + "\n"
        t += f"  {'Joueur':>12}  {'Cout total':>12}\n"
        t += "  " + "-" * 38 + "\n"

        for joueur in joueurs:
            cout = self.enchere.calculer_cout_joueur(joueur)  # Calcul du coût individuel
            t += f"  {joueur:>12}  {cout:>10.2f} euros\n"

        t += "  " + "-" * 38 + "\n"
        t += f"  {'TOTAL':>12}  {self.enchere.calculer_recette_vendeur():>10.2f} euros\n"

        self._ecrire_analyse(t)

    def _afficher_succ_pred(self):
        """
        Affiche le successeur et le prédécesseur de chaque prix dans l'ABR.
        Utile pour comprendre la navigation dans l'arbre et l'algorithme de recherche.
        """
        if self.enchere.abr.est_vide():
            self._ecrire_analyse("Aucune donnee disponible.\n")
            return

        noeuds = self.enchere.abr.parcours_infixe()  # Tous les nœuds triés par prix croissant

        t  = "\n  SUCCESSEURS ET PREDECESSEURS\n  " + "-" * 52 + "\n"
        t += f"  {'Prix':>6}  {'Predecesseur':>14}  {'Successeur':>12}\n"
        t += "  " + "-" * 52 + "\n"

        for noeud in noeuds:
            pred = self.enchere.abr.predecesseur(noeud.prix)  # Plus grand prix < prix courant
            succ = self.enchere.abr.successeur(noeud.prix)    # Plus petit prix > prix courant

            pred_str = str(pred.prix) if pred else "---"   # "---" si aucun prédécesseur
            succ_str = str(succ.prix) if succ else "---"   # "---" si aucun successeur

            t += f"  {noeud.prix:>6}  {pred_str:>14}  {succ_str:>12}\n"

        self._ecrire_analyse(t)

    def _jouer_humain(self):
        """
        Lance une manche en mode Humain vs IA :
        Le joueur humain soumet son prix, les IA jouent selon leur stratégie.
        On affiche le résultat complet avec un conseil stratégique.
        """
        nom = self.entry_nom.get().strip()  # Récupération et nettoyage du nom saisi

        if not nom:
            self._ecrire_humain("Entrez votre nom avant de jouer.\n")
            return

        try:
            prix_humain = int(self.entry_prix.get())  # Conversion du prix saisi en entier
        except ValueError:
            self._ecrire_humain("Prix invalide : entrez un nombre entier.\n")
            return

        prix_max = self.var_prix_max.get()
        if prix_humain < 0 or prix_humain > prix_max:
            self._ecrire_humain(f"Prix hors limite : choisissez entre 0 et {prix_max}.\n")
            return

        # Création d'une nouvelle manche dédiée à ce tour
        manche = Enchere(cout_base=self.var_cout_base.get(), alpha=self.var_alpha.get())
        manche.ajouter_mise(nom, prix_humain)  # Ajout de la mise du joueur humain

        # Génération des mises des adversaires IA
        nb_ia    = self.var_nb_joueurs.get()   # Nombre d'adversaires IA
        mode_ia  = self.combo_ia.get()         # Mode de jeu des IA (Mixte, Aléatoire, etc.)

        for i in range(nb_ia):
            nom_ia = f"IA_{i+1:02d}"  # Nom de l'IA : IA_01, IA_02, ..., IA_20

            # Sélection de la stratégie de l'IA selon le mode choisi
            if mode_ia == "Aleatoire":
                prix_ia = strategie_aleatoire(prix_max)
            elif mode_ia == "Conservative":
                prix_ia = strategie_conservative(prix_max)
            elif mode_ia == "Agressive":
                prix_ia = strategie_agressive(prix_max)
            else:
                # Mode Mixte : chaque IA choisit une stratégie différente au hasard
                strategie_ia = random.choice([strategie_aleatoire, strategie_conservative, strategie_agressive])
                prix_ia = strategie_ia(prix_max)

            manche.ajouter_mise(nom_ia, prix_ia)  # Ajout de la mise de l'IA

        # Calcul et affichage des résultats de cette manche
        gagnant      = manche.trouver_gagnant()
        recette      = manche.calculer_recette_vendeur()
        cout_humain  = manche.calculer_cout_joueur(nom)

        t  = "\n" + "=" * 55 + "\n"
        t += f"  MANCHE : {nom} vs {nb_ia} IAs ({mode_ia})\n"
        t += "=" * 55 + "\n"
        t += f"  Votre mise       : {prix_humain}  (cout : {cout_humain:.2f} euros)\n"
        t += f"  Recette vendeur  : {recette:.2f} euros\n\n"

        if gagnant:
            prix_g, joueur_g = gagnant
            if joueur_g == nom:
                # Le joueur humain a gagné !
                t += f"  VOUS AVEZ GAGNE avec le prix {prix_g} !\n"
                t += f"  Felicitations : c'etait le plus bas prix unique.\n"
            else:
                # Le joueur humain n'a pas gagné
                t += f"  Vous n'avez pas gagne cette manche.\n"
                t += f"  Gagnant : {joueur_g} avec le prix {prix_g}\n"
                # Conseil : expliquer pourquoi le joueur humain a perdu
                noeud_h = manche.abr.rechercher(prix_humain)
                if noeud_h and len(noeud_h.joueurs) > 1:
                    t += f"  Votre prix ({prix_humain}) n'etait pas unique ({len(noeud_h.joueurs)} joueurs).\n"
        else:
            t += "  Aucun gagnant --- Manche annulee (aucun prix unique)\n"

        t += "=" * 55 + "\n"
        self._ecrire_humain(t)

    # ==========================================================
    # MÉTHODES UTILITAIRES D'ÉCRITURE DANS LES ZONES DE TEXTE
    # ==========================================================

    def _ecrire_enchere(self, texte):
        """Ajoute du texte à la fin de la zone de l'onglet Enchère et scrolle vers le bas."""
        self.texte_enchere.insert("end", texte)  # Insertion à la fin
        self.texte_enchere.see("end")            # Défilement automatique vers le bas

    def _ecrire_simulation(self, texte):
        """Ajoute du texte à la fin de la zone de l'onglet Simulation."""
        self.texte_simulation.insert("end", texte)
        self.texte_simulation.see("end")

    def _ecrire_analyse(self, texte):
        """Ajoute du texte à la fin de la zone de l'onglet Analyse."""
        self.texte_analyse.insert("end", texte)
        self.texte_analyse.see("end")

    def _ecrire_humain(self, texte):
        """Ajoute du texte à la fin de la zone de l'onglet Humain vs IA."""
        self.texte_humain.insert("end", texte)
        self.texte_humain.see("end")


# ==========================================================
# POINT D'ENTRÉE DU PROGRAMME
# ==========================================================

if __name__ == "__main__":
    # Ce bloc s'exécute uniquement si l'on lance directement ce fichier (python3 interface.py)
    app = ApplicationLowBid()  # Création de l'instance de la fenêtre principale
    app.mainloop()             # Lancement de la boucle d'événements Tkinter (affiche la fenêtre)
