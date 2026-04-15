# APP2 — LowBid : Qui perd gagne !

> Plateforme d'enchères inversées : le prix le plus bas **unique** remporte la mise.

## Équipe
- malmezat-gif
- tmalmeu

---

## Contexte

Dans une enchère inversée LowBid, chaque joueur propose un prix. Le gagnant est celui qui soumet le prix le plus bas **et** qui est le seul à l'avoir proposé. Chaque mise a un coût calculé selon la formule :



avec  et .

---

## Fonctionnalités

- **Structure ABR** : insertion et recherche en O(log n) en moyenne
- **4 stratégies de jeu** : aléatoire, conservative, agressive, adaptative
- **Simulation multi-manches** : jusqu'à 500 manches avec statistiques par stratégie
- **Interface graphique** : 4 onglets (Enchère, Simulation, Analyse, Humain vs IA)
- **Chargement CSV** : support de 2 formats de fichiers de données
- **Détection de dégénérescence** : alerte si l'ABR devient déséquilibré

---

## Structure du projet



---

## Installation

Defaulting to user installation because normal site-packages is not writeable
Collecting customtkinter
  Downloading customtkinter-5.2.2-py3-none-any.whl.metadata (677 bytes)
Collecting darkdetect (from customtkinter)
  Downloading darkdetect-0.8.0-py3-none-any.whl.metadata (3.6 kB)
Requirement already satisfied: packaging in /usr/local/lib/python3.10/dist-packages (from customtkinter) (26.0)
Downloading customtkinter-5.2.2-py3-none-any.whl (296 kB)
Downloading darkdetect-0.8.0-py3-none-any.whl (9.0 kB)
Installing collected packages: darkdetect, customtkinter

Successfully installed customtkinter-5.2.2 darkdetect-0.8.0

Python 3.8+ requis. Aucune autre dépendance externe.

---

## Lancement



---

## Choix techniques

| Décision | Justification |
|---|---|
| ABR plutôt que liste triée | Insertion O(log n) en moyenne vs O(n) |
| Parcours infixe pour le gagnant | Nœuds triés par prix en O(n) |
| Successeur/Prédécesseur itératif | O(h) sans récursion, plus lisible |
| Threading pour la simulation | Évite de geler l'interface Tkinter |
| Base64 + TextDecoder | Injection UTF-8 fiable dans CodeMirror |

---

## Réponses aux questions du cahier des charges

**Q1 — Complexité de l'insertion dans l'ABR**
- Moyenne : O(log n) si l'arbre est équilibré (mises aléatoires)
- Pire cas : O(n) si les prix sont insérés en ordre croissant (arbre dégénéré)

**Q2 — Trouver le plus bas prix unique**
- Parcours infixe → nœuds en ordre croissant
- On retourne le premier nœud avec exactement 1 joueur
- Complexité : O(n) dans tous les cas

**Q3 — Successeur et prédécesseur**
-  : minimum du sous-arbre droit, ou premier ancêtre « à gauche »
-  : symétrique
- Complexité : O(h) où h = hauteur de l'arbre

**Q4 — Dégénérescence de l'ABR**
- Si les prix sont insérés en ordre croissant (stratégie conservative), l'ABR devient une liste chaînée → hauteur = n
- Détection : comparer h à log₂(n+1)
- Solution recommandée : AVL ou dictionnaire + tri

**Q5 — Comparaison des stratégies (simulation 500 manches)**
- **Agressive** : fort taux de victoire car les prix bas sont plus souvent uniques
- **Conservative** : recette vendeur maximale (prix élevés = coûts élevés)
- **Adaptative** : performance variable selon l'historique disponible
- **Aléatoire** : référence neutre, taux de victoire ≈ 1/nb_joueurs

---

## Licence

Projet académique — APP2, Polytechnique Montréal.
