# APP2 - LowBid

Projet realise en groupe par Titouan, Illyas, Maxime et Thibault.

Le principe du jeu est simple : chaque joueur propose un prix entier superieur ou egal a 0. Le gagnant est celui qui a propose le plus petit prix unique. Une mise n'est pas gratuite. Son cout est calcule avec la formule :

`cout_mise(prix) = cout_base + alpha / (prix + 1)`

Plus le prix est bas, plus la mise coute cher. Cela evite que tout le monde joue 0.

## Ce que fait le programme

- charger un fichier CSV de mises
- generer un jeu de donnees de demonstration
- stocker les prix dans un ABR
- afficher l'etat de l'enchere en ordre croissant
- trouver le plus bas prix unique
- calculer les couts des joueurs et la recette du vendeur
- afficher la distribution des prix
- donner le successeur et le predecesseur d'un prix
- simuler au moins 500 manches avec plusieurs strategies
- faire jouer un humain contre des IA

## Fichiers principaux

- `abr.py` : l'arbre binaire de recherche
- `encheres.py` : une manche complete
- `outils.py` : formule de cout, CSV et generation de donnees
- `strategies.py` : les strategies de joueurs
- `simulation.py` : la simulation de plusieurs manches
- `interface.py` : l'interface graphique en `tkinter`
- `test_lowbid.py` : quelques verifications automatiques

## Lancer le projet

Pour ouvrir l'interface :

```bash
python3 interface.py
```

Pour lancer la verification automatique :

```bash
python3 -m unittest test_lowbid.py
```

## Choix qu'on a gardes

On a volontairement garde un code simple. L'objectif etait d'avoir quelque chose qu'on peut expliquer facilement a l'oral sans donner l'impression d'un projet trop complique.

- On utilise un ABR parce qu'il garde les prix ordonnes pendant les insertions.
- Quand plusieurs joueurs ont le meme prix, on les garde dans la meme liste dans le noeud.
- On ne fait pas de tri Python pour trouver le gagnant principal. On passe par le parcours infixe de l'ABR.
- L'interface est faite avec `tkinter` standard pour rester legere et facile a lancer.

## Reponses courtes au sujet

- Le prix 0 n'est pas une strategie dominante parce qu'il coute tres cher et il risque d'etre choisi par plusieurs joueurs.
- Le systeme n'est pas a somme nulle : le vendeur gagne de l'argent meme si personne ne gagne l'objet.
- Pour trouver le gagnant, il faut connaitre les prix joues et savoir combien de joueurs ont choisi chaque prix.
- Un ABR simple peut se degenerer si les insertions arrivent deja presque triees.
- Pour eviter cela, on pourrait utiliser un AVL ou une autre structure equilibree.

## Remarque

Le code a ete simplifie volontairement pour privilegier la lisibilite. Les docstrings expliquent surtout l'ordre des etapes, afin qu'un debutant puisse suivre plus facilement.
