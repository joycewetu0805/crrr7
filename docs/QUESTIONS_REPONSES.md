# FraudShield AI — 10 questions pour maîtriser et défendre le projet

Ce document répond simplement aux 10 questions les plus probables sur le
projet, en distinguant toujours **ce qui a été réellement implémenté et
testé** de ce qui a été **seulement envisagé** — c'est exactement ce genre
de distinction qu'un jury vérifie en creusant.

---

## 1. Qu'est-ce que FraudShield AI ?

**En une phrase :** une application qui reçoit une transaction, la fait
analyser par un modèle de Machine Learning, et affiche en temps réel un
score de risque et une alerte si nécessaire.

**Plus en détail :** FraudShield AI est composé de 4 briques qui
communiquent entre elles :
1. Un **dataset** synthétique de transactions (pour entraîner le modèle)
2. Un **modèle de Machine Learning** (Random Forest) qui calcule une
   probabilité de fraude
3. Une **API** (FastAPI) qui reçoit les transactions, appelle le modèle
   et enregistre le résultat en base de données
4. Un **tableau de bord** (React) qui affiche les statistiques, l'historique
   et les alertes

**Comment répondre simplement :** "C'est un prototype qui automatise la
première étape de détection de fraude : au lieu qu'un humain vérifie
chaque transaction, un modèle entraîné sur des exemples calcule un score
de risque instantanément, et seules les transactions suspectes remontent
à un analyste."

---

## 2. Quel problème ton projet cherche-t-il à résoudre ?

**En une phrase :** détecter automatiquement les transactions frauduleuses
parmi un grand volume de transactions légitimes, sans règles fixes trop
rigides.

**Plus en détail :** avec la digitalisation des paiements (carte, virement,
Mobile Money), le volume de transactions à surveiller a explosé. Une
vérification manuelle de chaque transaction est impossible. Les systèmes
à **règles fixes** ("bloquer si montant > 1000€") sont simples mais ont
deux défauts : ils ratent les fraudes qui restent sous le seuil, et ils
bloquent des clients légitimes qui dépassent le seuil pour une raison
normale (un achat exceptionnel, par exemple).

**Comment répondre simplement :** "Une règle fixe regarde un seul chiffre
isolément. Le problème, c'est qu'une fraude se reconnaît souvent à la
**combinaison** de plusieurs signaux faibles — montant inhabituel + pays
étranger + heure de nuit — qu'une règle simple ne peut pas capturer
facilement."

---

## 3. Pourquoi utiliser l'IA / Machine Learning ?

**En une phrase :** parce que le ML apprend à combiner plusieurs facteurs
automatiquement, et produit un score continu (une probabilité) plutôt
qu'une décision binaire.

**Plus en détail :** un modèle de Machine Learning, entraîné sur des
milliers d'exemples de transactions légitimes et frauduleuses, apprend
lui-même **quelles combinaisons de facteurs** sont associées à la fraude
— sans qu'on ait besoin de coder ces règles à la main. Il produit une
**probabilité** (par exemple 82 %), ce qui permet de prioriser (bloquer
les cas critiques, mettre en revue manuelle les cas ambigus) au lieu d'un
simple oui/non.

**Comment répondre simplement :** "Le ML remplace des dizaines de règles
`si...alors` écrites à la main par un modèle qui apprend ces règles tout
seul à partir des données, et qui les combine de façon plus fine qu'un
humain ne le ferait."

**Si le jury insiste — "l'IA n'est pas magique, qu'est-ce qu'elle fait
concrètement ?"** : "Elle calcule, pour chaque transaction, à quel point
elle ressemble statistiquement aux fraudes qu'elle a vues à
l'entraînement, en tenant compte de plusieurs variables en même temps."

---

## 4. Quelles données sont analysées ?

**En une phrase :** 9 variables calculées à partir de la transaction et de
l'historique du compte — aucune donnée bancaire réelle.

**Le détail réellement utilisé par le modèle :**

| Variable | Ce qu'elle capture |
|---|---|
| `montant` | Le montant de la transaction |
| `montant_moyen_compte` | La dépense moyenne habituelle de ce compte |
| `ecart_montant` | Le ratio entre les deux — un montant "normal dans l'absolu" peut être anormal *pour ce compte précis* |
| `heure` | L'heure de la transaction |
| `heure_nuit` | Transaction entre 0h et 6h ou non |
| `pays_transaction` / `pays_habituel_compte` | Le pays de la transaction vs le pays habituel |
| `pays_inhabituel` | Les deux pays sont-ils différents ? |
| `nb_transactions_1h` | Nombre de transactions du même compte dans l'heure précédente (vélocité — repère les rafales) |
| `type_transaction`, `canal` | Achat en ligne, retrait DAB, virement... / web, mobile, POS, DAB |

**Comment répondre simplement :** "Le modèle ne regarde jamais un montant
dans l'absolu, il le compare toujours à l'historique du compte — c'est
ça qui rend le score pertinent plutôt qu'un seuil arbitraire."

**Attention à cette question piège :** *"Vous stockez des noms de bénéficiaire, des numéros de téléphone ?"* → Non, aucune de ces données n'existe dans le prototype ; ce n'est pas une omission technique, ce sont des variables qui n'ont simplement jamais été implémentées (voir Q10).

---

## 5. Comment le système décide qu'une transaction est suspecte ?

**En une phrase :** le modèle calcule une probabilité de fraude entre 0 et
1, et deux seuils fixes la transforment en 3 niveaux.

**Le mécanisme exact :**
```
probabilité < 0,30   →  LÉGITIME  (vert)
0,30 ≤ probabilité < 0,70  →  SUSPECT  (orange)
probabilité ≥ 0,70   →  FRAUDE  (rouge)
```

**Comment répondre simplement :** "Le modèle ne dit jamais juste
'fraude/pas fraude'. Il sort un pourcentage, et ce pourcentage est ensuite
découpé en 3 zones : en dessous de 30 % on ne fait rien, entre 30 et 70 %
on recommande une vérification humaine, au-dessus de 70 % c'est une
alerte prioritaire."

**Si le jury demande "pourquoi 30 et 70, pas 20 et 80 ?"** : "Ce sont des
seuils de démonstration, choisis raisonnablement mais pas calibrés sur un
vrai coût métier. Dans un déploiement réel, on les ajusterait selon le
coût d'une fraude non détectée comparé au coût d'une vérification
manuelle inutile — c'est une seule constante à changer dans le code."

---

## 6. Quels modèles ML as-tu utilisés / proposés ?

**Utilisés et réellement comparés (avec des métriques mesurées) :**
- Régression Logistique
- Arbre de Décision
- **Random Forest** → modèle retenu

**Proposés dans la phase de conception, mais non implémentés :**
- XGBoost
- Isolation Forest

**Comment répondre simplement :** "J'ai entraîné et comparé 3 modèles sur
le même jeu de données, avec les mêmes métriques, et j'ai choisi le
meilleur sur des critères objectifs — pas au hasard. XGBoost et Isolation
Forest avaient été envisagés à l'origine mais n'ont pas été implémentés
dans cette version ; je le dis clairement plutôt que de laisser croire
qu'ils font partie du prototype."

**Résultats réels (jeu de test, jamais vu à l'entraînement) :**

| Modèle | Precision | Recall | F1-score | ROC-AUC |
|---|---|---|---|---|
| Régression Logistique | 0,427 | 0,927 | 0,585 | 0,980 |
| Arbre de Décision | 0,658 | 0,939 | 0,774 | 0,966 |
| **Random Forest** | **0,696** | **0,951** | **0,804** | **0,997** |

---

## 7. À quoi servent Random Forest, XGBoost et Isolation Forest ?

Trois familles différentes — utile de savoir les distinguer même si un
seul a été implémenté :

**Random Forest** (✅ implémenté et retenu) — un grand nombre d'arbres de
décision légèrement différents (chacun entraîné sur un sous-échantillon
aléatoire des données) votent, et la majorité l'emporte. Avantage :
robuste au sur-apprentissage, capture des relations non linéaires
(exemple : "montant élevé" n'est risqué que *combiné* à "pays inhabituel"),
et reste raisonnablement rapide à entraîner. C'est un standard pour les
données tabulaires comme les transactions.

**XGBoost** (❌ envisagé, non implémenté) — même famille (des arbres),
mais construits **séquentiellement** : chaque nouvel arbre essaie de
corriger les erreurs des arbres précédents (boosting). Souvent légèrement
plus performant que Random Forest sur de gros volumes, mais plus long à
régler (plus de paramètres) et plus sensible au sur-apprentissage sur un
petit dataset. **Pourquoi il n'a pas été utilisé ici :** avec 8 000
transactions seulement, Random Forest donnait déjà un excellent ROC-AUC
(0,997) — ajouter la complexité de XGBoost n'était pas justifié pour ce
volume, et le temps du hackathon a été investi ailleurs (API, dashboard).

**Isolation Forest** (❌ envisagé, non implémenté) — un modèle
**non supervisé** : contrairement aux trois précédents, il n'a pas besoin
de savoir à l'avance quelles transactions sont frauduleuses. Il isole les
points "atypiques" en mesurant à quelle vitesse ils se séparent du reste
des données dans des arbres aléatoires — une transaction isolée
rapidement est jugée anormale. **Intérêt qu'il aurait apporté :** détecter
des fraudes dont le *pattern* n'a jamais été vu à l'entraînement
(contrairement à Random Forest qui ne reconnaît que ce qu'il a appris).
C'est la perspective d'amélioration la plus citée dans le rapport de
limites du projet.

**Comment répondre simplement :** "Random Forest et XGBoost apprennent
tous les deux à partir d'exemples étiquetés fraude/pas-fraude, juste avec
une méthode d'entraînement différente. Isolation Forest est complètement
différent : il n'a pas besoin d'étiquettes, il repère juste ce qui sort
du lot."

---

## 8. Qu'est-ce que le score de risque ?

**En une phrase :** la probabilité, calculée par le modèle Random Forest,
qu'une transaction donnée soit une fraude — un nombre entre 0 et 1
(affiché en %).

**D'où il vient concrètement :** le modèle a appris, sur les 8 000
transactions d'entraînement, la relation statistique entre les 9
variables (Q4) et l'étiquette fraude/légitime. Pour une nouvelle
transaction, la méthode `predict_proba` de scikit-learn renvoie
directement cette probabilité — ce n'est pas une formule ni un
pourcentage inventé, c'est la sortie mathématique du modèle entraîné.

**Exemple réel testé sur le prototype :** un virement de 1500€ vers le
Nigeria à 3h du matin, sur un compte dont la moyenne habituelle est de
45€, obtient un score de 96,3 % → classé FRAUDE.

**Comment répondre simplement :** "C'est la sortie brute du modèle, pas
une note calculée après coup. Le modèle a vu des milliers d'exemples et
'sait' statistiquement à quel point telle combinaison de facteurs
ressemble aux fraudes qu'il a apprises."

---

## 9. À quoi servent les alertes et le dashboard ?

**En une phrase :** transformer un score isolé en outil de travail pour un
analyste — prioriser ce qui mérite une attention humaine.

**Le dashboard regroupe 4 choses :**
1. **Des cartes KPI** (total de transactions, taux de fraude, score moyen…)
   pour une vue d'ensemble immédiate
2. **Un panneau d'alertes** qui remonte automatiquement toute transaction
   suspecte ou frauduleuse, triée par risque décroissant
3. **Deux graphiques** (répartition par risque, montants récents) pour
   visualiser les tendances
4. **Un historique** complet des transactions analysées, avec leur statut

**Pourquoi c'est important, pas juste "joli" :** un score seul (ex : 82 %)
n'est utile à personne s'il reste caché dans une base de données. Le
dashboard rend ce score **actionnable** : un analyste voit en un coup
d'œil les 5 dernières alertes, sans avoir à interroger l'API à la main.

**Comment répondre simplement :** "Le modèle produit un chiffre, le
dashboard transforme ce chiffre en décision opérationnelle — c'est la
différence entre un modèle de recherche et un outil qu'un analyste peut
réellement utiliser tous les jours."

---

## 10. Quelles sont les limites de ton projet ?

Assumées et documentées plutôt que dissimulées — un jury qui les trouve
lui-même après que tu les aies caché fait bien plus mal que le fait de
les présenter toi-même.

- **Données synthétiques**, pas de vraies transactions — le dataset
  (8 000 lignes, 300 comptes) a été généré avec des règles probabilistes,
  pas observé sur un système réel.
- **Explicabilité non implémentée** — le champ prévu pour expliquer
  *pourquoi* une transaction est signalée existe dans la base de données
  mais n'est jamais rempli. SHAP avait été envisagé, pas fait.
- **Isolation Forest non implémenté** — le système ne détecte que des
  patterns de fraude qu'il a déjà vus à l'entraînement, pas des fraudes
  totalement inédites.
- **Cas limite réel trouvé en testant** : un très petit montant par
  rapport à la moyenne du compte (ex. un café à 4,50€ sur un compte à 42€
  de moyenne) peut être classé "suspect" à tort, car il ressemble au
  pattern "test de carte volée" appris par le modèle.
- **Pas d'authentification sur l'API**, CORS ouvert à tous — acceptable
  pour une démo locale, à corriger avant tout déploiement réel.
- **SQLite non éprouvé à grande échelle** — testé jusqu'à 30 requêtes
  simultanées sans erreur, mais pas au volume d'un opérateur réel.
- **Seuils de risque (30 %/70 %) fixés arbitrairement**, pas calibrés sur
  un vrai coût métier (coût d'une fraude ratée vs coût d'une vérification
  inutile).

**Comment répondre simplement :** "Le prototype fait ce qu'il annonce
faire, mais je sais précisément ce qu'il ne fait pas encore, et pourquoi
— ce sont des choix de temps (hackathon), pas des angles morts que je
découvre devant vous."

---

## Résumé express (30 secondes, si le temps manque)

"FraudShield AI reçoit une transaction, compare son montant, son heure et
son pays à l'historique du compte, et un modèle Random Forest — entraîné
sur 8 000 transactions synthétiques et choisi après comparaison avec 2
autres modèles — calcule une probabilité de fraude. Cette probabilité est
traduite en 3 niveaux de risque, affichés en direct sur un dashboard avec
alertes. XGBoost, Isolation Forest et l'explicabilité SHAP avaient été
envisagés mais ne sont pas implémentés — ce sont mes prochaines pistes."
