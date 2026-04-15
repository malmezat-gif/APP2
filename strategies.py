# ============================================================
# strategies.py - Stratégies de joueurs pour la simulation
# Chaque stratégie est une fonction qui retourne un prix (entier >= 0).
# ============================================================

import random  # Module Python pour les choix aléatoires


def strategie_aleatoire(prix_max=50):
    """
    Stratégie aléatoire : le joueur choisit un prix entierement au hasard.
    C'est la stratégie de référence (baseline) pour les comparaisons.
    Aucune logique : chaque prix a la même probabilité d'être choisi.
    """
    return random.randint(0, prix_max)  # Tirage aléatoire uniforme dans [0, prix_max]


def strategie_conservative(prix_max=50):
    """
    Stratégie conservative : le joueur préfère les PRIX ELEVÉS (moitié supérieure).
    Avantage : la prime de risque est plus faible pour les grands prix.
    Inconvénient : le prix gagnant est souvent petit, donc victoires rares.
    """
    minimum = prix_max // 2  # On se limite à la moitié supérieure
    return random.randint(minimum, prix_max)  # Tirage dans la tranche haute


def strategie_agressive(prix_max=50):
    """
    Stratégie agressive : le joueur mise sur les PETITS PRIX (premier quart).
    Avantage : si son prix est unique, il gagnera probablement.
    Inconvénient : les petits prix coûtent cher (prime de risque élevée).
    """
    maximum = prix_max // 4  # On se limite au quart inférieur
    return random.randint(0, maximum)  # Tirage dans la tranche basse


def strategie_adaptative(historique_prix, prix_max=50):
    """
    Stratégie adaptative : le joueur utilise l'historique pour choisir un prix PEU JOUÉ.
    Principe : éviter les prix que les autres choisissent souvent = maximiser
    la chance d'avoir un prix unique.
    historique_prix : liste de tous les prix joués lors des manches précédentes.
    """
    if not historique_prix:
        return random.randint(0, prix_max)  # Pas d'historique : jeu aléatoire

    # Comptage des occurrences de chaque prix dans l'historique
    comptage = {}  # Dictionnaire {prix: nombre de fois joué}
    for prix in historique_prix:
        if prix not in comptage:
            comptage[prix] = 0   # Initialisation
        comptage[prix] += 1      # Incrémentation

    # Sélection des prix peu joués (0 ou 1 occurrence)
    prix_rares = []
    for p in range(prix_max + 1):
        if comptage.get(p, 0) <= 1:  # Prix jamais ou rarement joué
            prix_rares.append(p)

    if prix_rares:
        return random.choice(prix_rares)  # On choisit parmi les prix rares
    else:
        return random.randint(0, prix_max)  # Repli aléatoire si tout a été joué


def strategie_humain(nom_joueur, prix_max=50):
    """
    Stratégie humaine : le joueur entre son prix au clavier (mode terminal).
    La fonction boucle jusqu'à obtenir une valeur entière valide dans [0, prix_max].
    """
    while True:
        try:
            saisie = input(f"  [{nom_joueur}] Entrez votre mise (entier entre 0 et {prix_max}) : ")
            prix = int(saisie)  # Conversion en entier (lève ValueError si invalide)
            if 0 <= prix <= prix_max:
                return prix  # Prix valide : on le retourne
            else:
                print(f"  [!] Prix invalide ! Choisissez entre 0 et {prix_max}.")
        except ValueError:
            print("  [!] Entree non reconnue. Tapez un nombre entier.")


# Dictionnaire des stratégies disponibles pour la simulation
# (sans strategie_adaptative car elle nécessite un argument supplémentaire)
STRATEGIES_DISPONIBLES = {
    "aleatoire"   : strategie_aleatoire,     # Tirage aléatoire pur
    "conservative": strategie_conservative,  # Préférence pour les grands prix
    "agressive"   : strategie_agressive,     # Préférence pour les petits prix
}
