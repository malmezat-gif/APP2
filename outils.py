import csv
import random


COUT_BASE = 1.0
ALPHA = 10.0
PRIX_MAX = 100

NB_MANCHES_SIMULATION = 500
NB_JOUEURS_DEFAUT = 20


def cout_mise(prix, cout_base=COUT_BASE, alpha=ALPHA):
    """
    Calcule le cout d'une mise.

    Dans l'ordre :
    - on verifie que le prix est correct
    - on applique la formule du sujet
    - on arrondit le resultat
    """
    if prix < 0:
        raise ValueError("Le prix doit etre superieur ou egal a 0.")

    cout = cout_base + alpha / (prix + 1)
    return round(cout, 2)


def charger_csv(chemin_fichier):
    """
    Charge un fichier CSV de mises.

    Formats acceptes :
    - joueur,prix
    - manche,joueur,prix

    La fonction lit ligne par ligne et transforme chaque ligne en tuple.
    """
    mises = []

    with open(chemin_fichier, newline="", encoding="utf-8") as fichier:
        lecteur = csv.reader(fichier)
        entete = next(lecteur, None)

        if entete is None:
            return mises

        entete = [colonne.strip().lower() for colonne in entete]

        for numero_ligne, ligne in enumerate(lecteur, start=2):
            if not ligne or not any(cellule.strip() for cellule in ligne):
                continue

            if entete == ["joueur", "prix"]:
                if len(ligne) != 2:
                    raise ValueError(f"Ligne {numero_ligne} invalide.")
                joueur = ligne[0].strip()
                prix = int(ligne[1])
                mises.append((joueur, prix))

            elif entete == ["manche", "joueur", "prix"]:
                if len(ligne) != 3:
                    raise ValueError(f"Ligne {numero_ligne} invalide.")
                manche = int(ligne[0])
                joueur = ligne[1].strip()
                prix = int(ligne[2])
                mises.append((manche, joueur, prix))

            else:
                raise ValueError(
                    "Le fichier doit commencer par 'joueur,prix' "
                    "ou 'manche,joueur,prix'."
                )

    return mises


def generer_mises_aleatoires(nb_joueurs, prix_max=PRIX_MAX):
    """
    Cree des donnees de demonstration.

    Pour chaque joueur :
    - on fabrique un nom simple
    - on choisit un prix au hasard
    - on ajoute le resultat dans la liste
    """
    mises = []

    for numero in range(1, nb_joueurs + 1):
        joueur = f"J{numero:02d}"
        prix = random.randint(0, prix_max)
        mises.append((joueur, prix))

    return mises
