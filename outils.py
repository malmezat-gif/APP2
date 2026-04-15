# ============================================================
# outils.py - Constantes et fonctions utilitaires du projet
# LowBid : "Qui perd gagne !" — Enchère inversée
# ============================================================

# --- Paramètres globaux de l'enchère (modifiables) ---

COUT_BASE = 1       # Coût fixe de participation à chaque mise (en euros)
ALPHA = 10          # Intensité de la prime de risque (plus alpha est grand, plus les petits prix coûtent cher)
PRIX_MAX = 100      # Prix maximum qu'un joueur peut proposer lors d'une mise

# --- Paramètres de simulation ---

NB_MANCHES_SIMULATION = 500   # Nombre de manches par défaut pour une simulation
NB_JOUEURS_DEFAUT = 20        # Nombre de joueurs par défaut dans une simulation


def cout_mise(prix, cout_base=COUT_BASE, alpha=ALPHA):
    """
    Calcule le coût d'une mise pour un prix donné.
    Formule officielle : cout_base + alpha / (prix + 1)
    Principe : plus le prix est bas, plus la mise est chère (prime de risque).
    """
    # Vérification que le prix est bien un entier positif ou nul (règle du jeu)
    if prix < 0:
        raise ValueError("Le prix doit être un entier >= 0")

    # Calcul du coût : coût fixe + prime de risque décroissante avec le prix
    cout = cout_base + alpha / (prix + 1)

    # On retourne le coût arrondi à 2 décimales (précision en euros)
    return round(cout, 2)


def charger_csv(chemin_fichier):
    """
    Charge un fichier CSV de mises (joueur, prix) ou (manche, joueur, prix).
    Retourne une liste de tuples selon le format détecté.
    """
    mises = []  # Liste qui contiendra les mises lues dans le fichier

    try:
        # Ouverture du fichier texte en lecture avec encodage UTF-8
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            lignes = f.readlines()  # Lecture de toutes les lignes d'un coup

        # La première ligne est l'en-tête (ex: "joueur,prix" ou "manche,joueur,prix")
        entete = lignes[0].strip().split(',')  # On découpe l'en-tête par virgule

        # Parcours de chaque ligne de données (on commence à la ligne 1 pour sauter l'en-tête)
        for ligne in lignes[1:]:
            elements = ligne.strip().split(',')  # Découpage de la ligne par virgule

            if not elements or elements == ['']:  # On ignore les lignes vides
                continue

            # Format avec numéro de manche : "manche,joueur,prix"
            if len(entete) == 3 and entete[0] == 'manche':
                manche = int(elements[0])       # Numéro de la manche (entier)
                joueur = elements[1].strip()    # Identifiant du joueur (chaîne)
                prix   = int(elements[2])       # Prix proposé (entier)
                mises.append((manche, joueur, prix))  # Ajout du triplet dans la liste

            # Format simple : "joueur,prix"
            elif len(entete) == 2:
                joueur = elements[0].strip()    # Identifiant du joueur
                prix   = int(elements[1])       # Prix proposé
                mises.append((joueur, prix))    # Ajout du couple dans la liste

        return mises  # On retourne la liste complète des mises chargées

    except FileNotFoundError:
        print(f"Erreur : fichier '{chemin_fichier}' introuvable.")
        return []

    except ValueError as e:
        print(f"Erreur de format dans le fichier CSV : {e}")
        return []


def generer_mises_aleatoires(nb_joueurs, prix_max=PRIX_MAX):
    """
    Génère un jeu de données aléatoire pour démonstration ou simulation.
    Chaque joueur propose un seul prix aléatoire entre 0 et prix_max.
    Retourne une liste de tuples (joueur, prix).
    """
    import random  # Module Python standard pour la génération de nombres aléatoires

    mises = []  # Liste qui contiendra les mises générées

    for i in range(nb_joueurs):
        joueur = f"J{i+1:02d}"              # Nom du joueur au format J01, J02, ..., J99
        prix   = random.randint(0, prix_max)  # Prix aléatoire entre 0 et prix_max inclus
        mises.append((joueur, prix))         # Ajout de la mise dans la liste

    return mises  # On retourne la liste des mises générées
