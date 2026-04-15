import random


def strategie_aleatoire(prix_max=50):
    """
    Choisit un prix au hasard entre 0 et prix_max.
    """
    return random.randint(0, prix_max)


def strategie_conservative(prix_max=50):
    """
    Prefere les prix plus hauts.

    Ici on tire seulement dans la moitie haute.
    """
    minimum = prix_max // 2
    return random.randint(minimum, prix_max)


def strategie_agressive(prix_max=50):
    """
    Prefere les petits prix.

    Ici on tire seulement dans le premier quart.
    """
    maximum = max(1, prix_max // 4)
    return random.randint(0, maximum)


def strategie_adaptative(historique_prix, prix_max=50):
    """
    Cherche un prix peu utilise dans l'historique.

    Dans l'ordre :
    - on compte les anciens prix
    - on garde les prix les moins vus
    - on en choisit un au hasard
    """
    if not historique_prix:
        return random.randint(0, prix_max)

    compteurs = {}
    for prix in historique_prix:
        compteurs[prix] = compteurs.get(prix, 0) + 1

    plus_petit_compteur = min(compteurs.get(prix, 0) for prix in range(prix_max + 1))

    candidats = []
    for prix in range(prix_max + 1):
        if compteurs.get(prix, 0) == plus_petit_compteur:
            candidats.append(prix)

    return random.choice(candidats)


def strategie_humain(nom_joueur, prix_max=50):
    """
    Lit un prix au clavier.

    La boucle continue tant que la saisie n'est pas correcte.
    """
    while True:
        try:
            saisie = input(f"{nom_joueur}, entre un prix entre 0 et {prix_max} : ")
            prix = int(saisie)

            if 0 <= prix <= prix_max:
                return prix

            print(f"Choisis un prix entre 0 et {prix_max}.")

        except ValueError:
            print("Tu dois entrer un nombre entier.")


STRATEGIES_DISPONIBLES = {
    "aleatoire": strategie_aleatoire,
    "conservative": strategie_conservative,
    "agressive": strategie_agressive,
}
