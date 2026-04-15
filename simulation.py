# ============================================================
# simulation.py - Simulation multi-manches de l'enchère LowBid
# Compare les stratégies sur un grand nombre de manches (>= 500)
# ============================================================

import random
from encheres  import Enchere
from strategies import (
    strategie_aleatoire,
    strategie_conservative,
    strategie_agressive,
    strategie_adaptative
)
from outils import COUT_BASE, ALPHA


def simuler_une_manche(joueurs_config, cout_base=COUT_BASE, alpha=ALPHA, prix_max=50):
    """
    Simule UNE SEULE manche d'enchère.
    joueurs_config : {nom_joueur: (fonction_strategie, historique_prix)}
    Retourne un dictionnaire : gagnant, recette, nb_mises, hauteur_abr.
    """
    enchere = Enchere(cout_base=cout_base, alpha=alpha)  # Manche vide

    for joueur, (strategie, historique) in joueurs_config.items():
        if strategie == strategie_adaptative:
            prix = strategie(historique, prix_max)  # Strat. adaptative : besoin de l'historique
        else:
            prix = strategie(prix_max)              # Autres stratégies : pas d'historique

        enchere.ajouter_mise(joueur, prix)  # Soumission de la mise
        historique.append(prix)             # Mémorisation pour les prochaines manches

    return {
        "gagnant"    : enchere.trouver_gagnant(),           # (prix, joueur) ou None
        "recette"    : enchere.calculer_recette_vendeur(),  # Recette du vendeur
        "nb_mises"   : enchere.abr.nb_total_mises(),       # Nb total de mises
        "hauteur_abr": enchere.abr.hauteur(),              # Hauteur de l'ABR
    }


def simuler_plusieurs_manches(
    strategies_equipes,     # {nom_strategie: fonction_strategie}
    nb_joueurs=20,          # Joueurs par manche
    nb_manches=500,         # Nombre de manches
    cout_base=COUT_BASE,
    alpha=ALPHA,
    prix_max=50,
):
    """
    Lance une simulation de nb_manches manches et compare les stratégies.
    Les joueurs sont assignés en rotation circulaire parmi les stratégies.
    Retourne un dictionnaire de statistiques par stratégie et pour le vendeur.
    """
    # Initialisation des compteurs par stratégie
    stats = {}
    for nom in strategies_equipes:
        stats[nom] = {
            "victoires"   : 0,    # Nombre de manches gagnées
            "gains_totaux": 0.0,  # Somme des prix gagnants
        }

    stats["vendeur"] = {
        "recette_totale"     : 0.0,  # Recette cumulée
        "manches_sans_gagnant": 0,   # Manches annulées
    }

    # Historiques par stratégie pour la stratégie adaptative
    historiques = {nom: [] for nom in strategies_equipes}
    noms_strategies = list(strategies_equipes.keys())

    # BOUCLE PRINCIPALE
    for _ in range(nb_manches):
        joueurs_config = {}
        for i in range(nb_joueurs):
            nom_strategie = noms_strategies[i % len(noms_strategies)]  # Rotation circulaire
            nom_joueur    = f"J{i+1:02d}"
            joueurs_config[nom_joueur] = (
                strategies_equipes[nom_strategie],
                historiques[nom_strategie],
            )

        resultat = simuler_une_manche(joueurs_config, cout_base, alpha, prix_max)
        stats["vendeur"]["recette_totale"] += resultat["recette"]

        if resultat["gagnant"] is None:
            stats["vendeur"]["manches_sans_gagnant"] += 1  # Manche annulée
        else:
            prix_gagnant, joueur_gagnant = resultat["gagnant"]
            try:
                num_gagnant = int(joueur_gagnant[1:]) - 1  # Ex: "J03" -> index 2
            except ValueError:
                num_gagnant = 0
            strategie_gagnante = noms_strategies[num_gagnant % len(noms_strategies)]
            stats[strategie_gagnante]["victoires"]     += 1
            stats[strategie_gagnante]["gains_totaux"]  += prix_gagnant

    return stats


def afficher_stats_simulation(stats, nb_manches):
    """
    Affiche les résultats de la simulation dans la console.
    """
    print("\n" + "=" * 65)
    print(f"  RESULTATS DE LA SIMULATION - {nb_manches} manches")
    print("=" * 65)

    for nom, donnees in stats.items():
        if nom == "vendeur":
            continue
        victoires  = donnees["victoires"]
        taux       = victoires / nb_manches * 100
        gain_moyen = donnees["gains_totaux"] / max(victoires, 1)
        print(f"\n  Strategie : {nom.upper()}")
        print(f"    Victoires   : {victoires} / {nb_manches} ({taux:.1f}%)")
        print(f"    Prix moyen  : {gain_moyen:.1f}")

    recette    = stats["vendeur"]["recette_totale"]
    annulees   = stats["vendeur"]["manches_sans_gagnant"]
    print(f"\n  VENDEUR")
    print(f"    Recette totale  : {recette:.2f} euros")
    print(f"    Recette/manche  : {recette/nb_manches:.2f} euros")
    print(f"    Manches annulees: {annulees} ({annulees/nb_manches*100:.1f}%)")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    # Test rapide en mode terminal (sans interface graphique)
    from strategies import strategie_aleatoire, strategie_conservative, strategie_agressive
    strategies = {
        "aleatoire"   : strategie_aleatoire,
        "conservative": strategie_conservative,
        "agressive"   : strategie_agressive,
    }
    resultats = simuler_plusieurs_manches(strategies, nb_joueurs=20, nb_manches=500)
    afficher_stats_simulation(resultats, 500)
