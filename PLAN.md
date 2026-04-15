# PLAN.md — APP2 LowBid « Qui perd gagne ! »

## Contexte
Plateforme d'enchères inversées : le plus bas prix **unique** remporte l'enchère.
Chaque mise a un coût : `cout_mise(prix) = cout_base + alpha/(prix+1)`.

---

## Décomposition en modules

| Fichier | Rôle |
|---|---|
| `outils.py` | Constantes, formule de coût, chargement CSV, génération aléatoire |
| `abr.py` | Structure de données ABR (Arbre Binaire de Recherche) |
| `encheres.py` | Moteur d'une manche (insertion, gagnant, recettes) |
| `strategies.py` | 4 stratégies de jeu (aléatoire, conservative, agressive, adaptative) |
| `simulation.py` | Simulation multi-manches, statistiques par stratégie |
| `interface.py` | GUI CustomTkinter, 4 onglets, threading |

---

## Choix techniques

| Décision | Justification |
|---|---|
| ABR plutôt que liste triée | Insertion O(log n) moyenne vs O(n) |
| Parcours infixe pour le gagnant | Renvoie les nœuds triés par prix en O(n) |
| Successeur/prédécesseur itératif | O(h) sans récursion, plus lisible |
| Threading pour la simulation | Évite de geler l'interface Tkinter |
| Base64 + TextDecoder pour GitHub | Injection UTF-8 fiable dans CodeMirror 6 |

---

## Réponses aux questions du cahier des charges

### Q1 — Complexité de l'insertion dans l'ABR
- Moyenne : **O(log n)** si l'arbre est équilibré (mises aléatoires)
- Pire cas : **O(n)** si les prix sont insérés en ordre croissant (arbre dégénéré)

### Q2 — Trouver le plus bas prix unique
- Parcours **infixe** → nœuds en ordre croissant
- On retourne le **premier nœud** avec 
- Complexité : **O(n)** dans tous les cas

### Q3 — Successeur et prédécesseur
- **Successeur(x)** : si x a un sous-arbre droit → minimum du sous-arbre droit ; sinon, remonter jusqu'au premier ancêtre « à gauche »
- **Prédécesseur(x)** : symétrique
- Complexité : **O(h)** où h = hauteur de l'arbre

### Q4 — Dégénérescence de l'ABR
- Si les prix sont insérés en ordre croissant (stratégie conservative), l'ABR devient une liste chaînée → hauteur = n
- Détection : comparer h à log₂(n+1)
- Solution : AVL ou dictionnaire + tri (non implémenté ici, mais signalé dans l'interface)

### Q5 — Comparaison des stratégies (simulation 500 manches)
- **Agressive** : fort taux de victoire car les prix bas sont plus souvent uniques
- **Conservative** : recette vendeur maximale (prix élevés = coûts élevés)
- **Adaptative** : performance variable selon l'historique disponible
- **Aléatoire** : référence neutre, taux de victoire ≈ 1/nb_joueurs

---

## Risques identifiés

| Risque | Impact | Mitigation |
|---|---|---|
| ABR dégénéré | Recherche O(n) | Signalement dans l'UI + conseil AVL |
| Aucun prix unique | Manche annulée | `trouver_gagnant()` retourne None |
| CSV mal formaté | Crash au chargement | `charger_csv()` gère les 2 formats |
| Interface gelée pendant simulation | UX dégradée | Thread daemon séparé |

---

## Équipe
- malmezat-gif
- tmalmeu
