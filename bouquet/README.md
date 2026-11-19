# Bouquet ASCII 3D

Un bouquet de fleurs dessiné en caractères ASCII qui tourne en 3D, inspiré
des bouquets « terminal » qu'on voit passer sur TikTok — mais en version web,
avec 6 variantes à faire défiler.

| Variante       | Fleurs                                        |
| -------------- | --------------------------------------------- |
| Roses          | roses rouges et roses + gypsophile            |
| Lys            | lys stargazer, lys blancs, boutons            |
| Lilas          | grappes de lilas mauves et blancs             |
| Tulipes        | tulipes multicolores, papier kraft            |
| Tournesols     | tournesols de différentes tailles             |
| Bouquet mixte  | un peu de tout                                |

## Lancer

Aucun build, aucune dépendance : ouvre `index.html` dans un navigateur
(ou `python3 -m http.server` dans ce dossier puis http://localhost:8000).

## Navigation

- le bouquet sélectionné s'affiche en grand et pivote sur lui-même
- en bas, une rangée de miniatures (qui tournent aussi) : touche-en une pour l'afficher
- flèches ← → de chaque côté des miniatures
- swipe gauche / droite sur mobile
- flèches du clavier sur ordinateur

## Personnaliser

- `index.html#lilas` → ouvre directement une variante
  (`roses`, `lys`, `lilas`, `tulipes`, `tournesols`, `mixte`)

## Comment ça marche

1. Chaque fleur est modélisée en 3D par des surfaces paramétriques
   (pétales en spirale pour la rose, tépales recourbés pour le lys, grappe
   conique de mini-fleurs pour le lilas…) échantillonnées en nuage de points.
2. À chaque frame, les points sont tournés, projetés en perspective et
   placés dans une grille de caractères avec un z-buffer (seul le point le
   plus proche de chaque case est gardé).
3. La luminosité (normale · lumière) choisit le caractère dans une rampe
   du type `.,-~:;=!*#$@`, et la couleur du point est appliquée au caractère.
4. Une copie floutée du canvas donne l'effet lumineux.
