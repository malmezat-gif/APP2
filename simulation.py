from encheres import Enchere
from outils import ALPHA, COUT_BASE
from strategies import strategie_adaptative


def simuler_une_manche(
    joueurs,
    strategies_choisies,
    historiques,
    cout_base=COUT_BASE,
    alpha=ALPHA,
    prix_max=50,
):
    """
    Joue une seule manche.

    `joueurs` contient des couples (nom_du_joueur, nom_de_la_strategie).
    """
    enchere = Enchere(cout_base=cout_base, alpha=alpha)

    for nom_joueur, nom_strategie in joueurs:
        fonction = strategies_choisies[nom_strategie]

        if fonction is strategie_adaptative:
            prix = fonction(historiques[nom_strategie], prix_max)
        else:
            prix = fonction(prix_max)

        enchere.ajouter_mise(nom_joueur, prix)
        historiques[nom_strategie].append(prix)

    gagnant = enchere.trouver_gagnant()
    strategie_gagnante = None

    if gagnant is not None:
        _, joueur_gagnant = gagnant
        for nom_joueur, nom_strategie in joueurs:
            if nom_joueur == joueur_gagnant:
                strategie_gagnante = nom_strategie
                break

    return {
        "gagnant": gagnant,
        "strategie_gagnante": strategie_gagnante,
        "recette": enchere.calculer_recette_vendeur(),
        "hauteur_abr": enchere.abr.hauteur(),
    }


def simuler_plusieurs_manches(
    strategies_choisies,
    nb_joueurs=20,
    nb_manches=500,
    cout_base=COUT_BASE,
    alpha=ALPHA,
    prix_max=50,
):
    """
    Joue plusieurs manches et regroupe les statistiques.

    Dans l'ordre :
    - on repartit les joueurs entre les strategies
    - on joue chaque manche
    - on compte les victoires et la recette du vendeur
    """
    if not strategies_choisies:
        raise ValueError("Il faut au moins une strategie.")

    stats = {}
    for nom in strategies_choisies:
        stats[nom] = {
            "victoires": 0,
            "total_prix_gagnants": 0.0,
            "taux_victoire": 0.0,
            "prix_moyen_gagnant": 0.0,
        }

    stats["vendeur"] = {
        "recette_totale": 0.0,
        "recette_moyenne": 0.0,
        "manches_sans_gagnant": 0,
    }

    noms_strategies = list(strategies_choisies.keys())
    historiques = {nom: [] for nom in noms_strategies}
    joueurs = []

    for numero in range(1, nb_joueurs + 1):
        nom_joueur = f"J{numero:02d}"
        nom_strategie = noms_strategies[(numero - 1) % len(noms_strategies)]
        joueurs.append((nom_joueur, nom_strategie))

    for _ in range(nb_manches):
        resultat = simuler_une_manche(
            joueurs,
            strategies_choisies,
            historiques,
            cout_base=cout_base,
            alpha=alpha,
            prix_max=prix_max,
        )

        stats["vendeur"]["recette_totale"] += resultat["recette"]

        if resultat["strategie_gagnante"] is None:
            stats["vendeur"]["manches_sans_gagnant"] += 1
            continue

        prix_gagnant, _ = resultat["gagnant"]
        nom_strategie = resultat["strategie_gagnante"]
        stats[nom_strategie]["victoires"] += 1
        stats[nom_strategie]["total_prix_gagnants"] += prix_gagnant

    for nom in noms_strategies:
        victoires = stats[nom]["victoires"]
        total_prix = stats[nom]["total_prix_gagnants"]

        if victoires > 0:
            stats[nom]["prix_moyen_gagnant"] = round(total_prix / victoires, 2)

        stats[nom]["taux_victoire"] = round(victoires / nb_manches * 100, 2)

    stats["vendeur"]["recette_totale"] = round(stats["vendeur"]["recette_totale"], 2)
    stats["vendeur"]["recette_moyenne"] = round(
        stats["vendeur"]["recette_totale"] / nb_manches,
        2,
    )

    return stats


def texte_stats_simulation(stats, nb_manches):
    """
    Transforme les statistiques en texte lisible pour l'ecran.
    """
    lignes = []
    lignes.append(f"Resultats sur {nb_manches} manches")
    lignes.append("--------------------------------")

    for nom, donnees in stats.items():
        if nom == "vendeur":
            continue

        lignes.append(f"Strategie : {nom}")
        lignes.append(f"  Victoires : {donnees['victoires']}")
        lignes.append(f"  Taux de victoire : {donnees['taux_victoire']:.2f} %")
        lignes.append(
            f"  Prix moyen gagnant : {donnees['prix_moyen_gagnant']:.2f}"
        )

    vendeur = stats["vendeur"]
    lignes.append("")
    lignes.append("Vendeur")
    lignes.append(f"  Recette totale : {vendeur['recette_totale']:.2f} euros")
    lignes.append(f"  Recette moyenne : {vendeur['recette_moyenne']:.2f} euros")
    lignes.append(f"  Manches sans gagnant : {vendeur['manches_sans_gagnant']}")

    return "\n".join(lignes) + "\n"


if __name__ == "__main__":
    from strategies import (
        strategie_agressive,
        strategie_aleatoire,
        strategie_conservative,
    )

    strategies = {
        "aleatoire": strategie_aleatoire,
        "conservative": strategie_conservative,
        "agressive": strategie_agressive,
    }

    resultats = simuler_plusieurs_manches(strategies, nb_joueurs=20, nb_manches=500)
    print(texte_stats_simulation(resultats, 500))
