import os
import tempfile
import unittest

from abr import ABR
from encheres import Enchere
from outils import charger_csv, cout_mise
from simulation import simuler_plusieurs_manches
from strategies import strategie_aleatoire, strategie_conservative


class TestLowBid(unittest.TestCase):
    def test_cout_mise(self):
        self.assertEqual(cout_mise(0, 1, 10), 11.0)
        self.assertEqual(cout_mise(9, 1, 10), 2.0)

    def test_charger_csv_simple(self):
        descripteur, chemin = tempfile.mkstemp(suffix=".csv", text=True)

        try:
            with os.fdopen(descripteur, "w", encoding="utf-8") as fichier:
                fichier.write("joueur,prix\n")
                fichier.write("J1,3\n")
                fichier.write("J2,7\n")

            self.assertEqual(charger_csv(chemin), [("J1", 3), ("J2", 7)])
        finally:
            os.remove(chemin)

    def test_gagnant(self):
        enchere = Enchere()
        enchere.charger_depuis_liste(
            [
                ("J1", 1),
                ("J2", 1),
                ("J3", 2),
                ("J4", 5),
            ]
        )

        self.assertEqual(enchere.trouver_gagnant(), (2, "J3"))

    def test_successeur_et_predecesseur(self):
        abr = ABR()

        for joueur, prix in [("J1", 5), ("J2", 2), ("J3", 8), ("J4", 6)]:
            abr.inserer(prix, joueur)

        self.assertEqual(abr.predecesseur(6).prix, 5)
        self.assertEqual(abr.successeur(6).prix, 8)

    def test_suppression_conditionnelle(self):
        abr = ABR()
        abr.inserer(4, "J1")
        abr.inserer(4, "J2")

        self.assertTrue(abr.supprimer_joueur(4, "J1"))
        self.assertIsNotNone(abr.rechercher(4))

        self.assertTrue(abr.supprimer_joueur(4, "J2"))
        self.assertIsNone(abr.rechercher(4))

    def test_simulation(self):
        stats = simuler_plusieurs_manches(
            {
                "aleatoire": strategie_aleatoire,
                "conservative": strategie_conservative,
            },
            nb_joueurs=10,
            nb_manches=20,
            prix_max=15,
        )

        total_victoires = (
            stats["aleatoire"]["victoires"] + stats["conservative"]["victoires"]
        )

        self.assertLessEqual(total_victoires, 20)
        self.assertIn("vendeur", stats)
        self.assertGreaterEqual(stats["vendeur"]["recette_totale"], 0)


if __name__ == "__main__":
    unittest.main()
