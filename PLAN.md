# PLAN.md

## Groupe

- Titouan
- Illyas
- Maxime
- Thibault

## Idee generale

On veut simuler une enchere "plus bas prix unique gagne".

Pour chaque manche :

- les joueurs choisissent un prix entier
- les prix sont ranges dans un ABR
- on cherche le premier prix unique
- on calcule ce que chaque joueur paie
- on calcule la recette totale du vendeur

## Organisation des fichiers

- `abr.py`
  Le stockage des prix dans l'arbre.
- `encheres.py`
  Une manche complete avec les calculs.
- `outils.py`
  Les fonctions simples utiles partout.
- `strategies.py`
  Les choix possibles pour les joueurs.
- `simulation.py`
  Les comparaisons sur beaucoup de manches.
- `interface.py`
  L'affichage en `tkinter`.

## Ce qu'il faut pouvoir montrer

- insertion dans l'ABR
- parcours infixe
- recherche d'un prix
- recherche du plus bas prix unique
- successeur et predecesseur
- suppression conditionnelle d'une mise
- simulation de plusieurs manches
- comparaison de plusieurs strategies

## Reponses simples pour l'oral

- Pourquoi 0 n'est pas toujours le meilleur choix ?
  Parce que le prix 0 coute tres cher et risque d'etre choisi plusieurs fois.

- Le systeme est-il a somme nulle ?
  Non. Le vendeur gagne de l'argent avec les mises, meme si personne ne gagne.

- Quelles infos faut-il pour trouver le gagnant ?
  Il faut connaitre les prix joues et savoir combien de joueurs ont choisi chaque prix.

- Peut-on trouver le gagnant sans trier avec `sort` ?
  Oui. Le parcours infixe de l'ABR donne deja les prix dans l'ordre.

- Quand l'ABR devient-il mauvais ?
  Quand les valeurs arrivent dans un ordre presque trie. L'arbre devient trop haut.

- Comment faire mieux si besoin ?
  On pourrait utiliser un AVL ou une autre structure equilibree.

## Ce qu'on a choisi

- Code simple et assez court
- Noms de fonctions explicites
- Docstrings en francais simple
- Interface sobre pour rester facile a comprendre
- Verification automatique du coeur du projet avec `test_lowbid.py`

## Point de vigilance

L'interface a ete gardee volontairement simple. Le plus important pour le sujet reste la logique de l'ABR et le calcul du gagnant.
