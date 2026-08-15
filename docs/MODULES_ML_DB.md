# FraudShield AI — Modules Machine Learning & Base de données

Pour chaque module : ce qu'il fait, pourquoi il existe, comment il
fonctionne, les technologies utilisées, les questions de jury probables
et comment y répondre simplement.

---

# MODULE 1 : MACHINE LEARNING

## 1. Ce qu'il fait

Il transforme des transactions brutes (montant, heure, pays...) en une
**probabilité de fraude**. Concrètement, quatre scripts qui se suivent :

1. `generate_dataset.py` — génère un dataset synthétique de transactions
2. `features.py` — calcule les variables utiles au modèle
3. `train.py` — entraîne, compare et sauvegarde le meilleur modèle
4. `predictor.py` — charge ce modèle et note une nouvelle transaction

## 2. Pourquoi il existe

Sans lui, il faudrait coder des règles fixes à la main ("bloquer si
montant > 1000 €"). Ces règles sont rigides : elles ratent les fraudes
qui combinent plusieurs signaux faibles (montant moyen + pays inhabituel
+ heure de nuit) et bloquent des clients légitimes qui dépassent le
seuil pour une raison normale. Le module ML apprend ces combinaisons
directement à partir d'exemples, et produit un score continu plutôt
qu'un simple oui/non.

## 3. Comment il fonctionne

**Étape 1 — Génération des données** (`generate_dataset.py`) : crée 300
comptes fictifs avec un pays habituel et une dépense moyenne, puis 8 000
transactions. 5 % sont étiquetées frauduleuses selon des règles
**probabilistes** (pas systématiques) : montant nettement plus élevé,
pays à risque, heure de nuit, plusieurs transactions rapprochées — mais
chaque signal n'apparaît qu'avec une certaine probabilité, pour que les
classes légitime/fraude se chevauchent partiellement, comme dans la
réalité.

> Point important à connaître : la toute première version de ce
> générateur produisait des classes **parfaitement séparables**, et les
> 3 modèles obtenaient 100 % sur toutes les métriques. C'était un signal
> d'alerte (dataset trop facile), pas une bonne nouvelle — le générateur
> a été corrigé avant l'entraînement final.

**Étape 2 — Features** (`features.py`) : transforme les données brutes
en 9 variables, dont 3 calculées (`ecart_montant` = montant / moyenne du
compte, `heure_nuit`, `pays_inhabituel`). Ce fichier est **partagé**
entre l'entraînement et la prédiction en production — c'est volontaire :
utiliser deux calculs différents à l'entraînement et à l'inférence est
une source classique de bugs en Machine Learning.

**Étape 3 — Entraînement** (`train.py`) : sépare les données en 80 %
train / 20 % test (stratifié, pour garder la même proportion de fraude
dans les deux). Entraîne 3 modèles dans un même pipeline scikit-learn
(prétraitement + modèle, sauvegardés ensemble) : Régression Logistique,
Arbre de Décision, Random Forest. Mesure sur le jeu de test — jamais vu
à l'entraînement — la precision, le recall, le F1-score, le ROC-AUC et
la matrice de confusion de chacun. Sélectionne le meilleur sur le
**F1-score** (pas l'accuracy, trompeuse avec seulement 5 % de fraude).
Sauvegarde le pipeline retenu (`model.pkl`) et un rapport de métriques
(`metrics.json`).

**Étape 4 — Prédiction** (`predictor.py`) : charge `model.pkl` **une
seule fois** au démarrage du serveur (pas à chaque requête). La fonction
`predire_transaction(dict)` calcule les features, appelle
`predict_proba()` du pipeline, applique deux seuils (0,30 et 0,70) pour
transformer la probabilité en `legitime` / `suspect` / `fraude`.

## 4. Technologies utilisées

- **Python** — langage
- **pandas** — manipulation des données tabulaires
- **numpy** — génération aléatoire contrôlée (graine fixe = reproductible)
- **scikit-learn** — `Pipeline`, `ColumnTransformer`, `StandardScaler`,
  `OneHotEncoder`, `LogisticRegression`, `DecisionTreeClassifier`,
  `RandomForestClassifier`, métriques (`precision_score`, `recall_score`,
  `f1_score`, `roc_auc_score`, `confusion_matrix`)
- **joblib** — sauvegarde/chargement du pipeline entraîné

## 5. Questions de jury probables

- Pourquoi un dataset synthétique et pas des données réelles ?
- Pourquoi ces 3 modèles et pas XGBoost ou un réseau de neurones ?
- Comment as-tu choisi le modèle final, pas au hasard ?
- Le modèle est-il fiable ? Peux-tu le prendre en défaut ?
- Comment évites-tu que le modèle "triche" (data leakage) ?
- Pourquoi le F1-score plutôt que l'accuracy ?
- D'où viennent les seuils 30 % / 70 % ?
- Que se passe-t-il si le fichier model.pkl est manquant ou corrompu ?

## 6. Comment répondre simplement

**"Dataset synthétique, ça n'est pas de la triche ?"**
"Le dataset public de référence (Kaggle) a des variables anonymisées par
PCA — inexploitables pour expliquer une décision. J'ai préféré un
dataset synthétique avec des variables lisibles, généré avec du bruit
volontaire pour ne pas être irréaliste."

**"Pourquoi pas XGBoost ou un réseau de neurones ?"**
"Avec 8 000 lignes et 9 variables, Random Forest atteint déjà un
ROC-AUC de 0,997 — un réseau de neurones aurait besoin de bien plus de
données pour apporter quelque chose, et serait moins interprétable.
XGBoost avait été envisagé mais pas justifié pour ce volume."

**"Comment as-tu choisi le modèle final ?"**
"J'ai comparé les 3 sur le même jeu de test avec les mêmes métriques,
et j'ai choisi celui avec le meilleur F1-score — 0,80 pour Random Forest
contre 0,58 pour la régression logistique. C'est un choix mesuré, pas
une intuition."

**"Le modèle peut-il se tromper ?"**
"Oui, et j'ai un exemple concret : un petit montant, très inférieur à
la moyenne habituelle du compte (par exemple un café à 4,50 € sur un
compte à 42 € de moyenne), peut être classé 'suspect' à tort, car il
ressemble au pattern 'test de carte volée' appris par le modèle. C'est
documenté comme limite connue, pas découvert devant le jury."

**"F1-score vs accuracy ?"**
"Avec seulement 5 % de fraude, un modèle qui répond toujours 'légitime'
aurait déjà 95 % d'accuracy sans détecter une seule fraude. Le F1-score
pénalise à la fois les fraudes ratées et les fausses alertes."

**"D'où viennent les seuils 30/70 ?"**
"Choisis raisonnablement pour la démo, pas calibrés sur un vrai coût
métier — une seule constante à changer dans le code si besoin."

---

# MODULE 2 : BASE DE DONNÉES

## 1. Ce qu'il fait

Il conserve durablement 3 choses : les comptes clients, les transactions
qu'ils effectuent, et le résultat de l'analyse de chaque transaction
(score + statut). Sans lui, tout serait perdu au redémarrage du serveur.

## 2. Pourquoi il existe

Trois raisons concrètes : (1) sans historique persistant, impossible de
calculer la moyenne habituelle d'un compte — **la feature la plus
importante du modèle ML** ; (2) sans stockage, le tableau de bord
n'aurait aucune donnée à afficher ; (3) c'est la mémoire du système —
chaque transaction analysée doit rester consultable.

## 3. Comment il fonctionne

**Le schéma** (`schema.sql`), en SQLite, 3 tables :

- `comptes` (id, numero_compte, nom_titulaire, email, pays,
  statut_compte, date_creation)
- `transactions` (id, compte_id **FK**, montant `CHECK > 0`, devise,
  type_transaction, canal, marchand, pays_transaction, date_transaction)
- `analyses_fraude` (id, transaction_id **FK UNIQUE**, score_fraude
  `CHECK entre 0 et 1`, statut, modele_version, facteurs_influents,
  date_analyse)

**Les relations** : un compte a plusieurs transactions (1–N). Une
transaction a **exactement une** analyse (1–1, garanti par la contrainte
`UNIQUE` sur `transaction_id`) — séparée dans sa propre table plutôt que
d'ajouter des colonnes à `transactions`, pour ne jamais mélanger le fait
brut (la transaction) et le jugement du modèle (le score).

**Le script est idempotent** : `CREATE TABLE IF NOT EXISTS` permet de le
rejouer à chaque démarrage du serveur sans erreur. Les données de
démonstration (`seed.sql`) ne sont insérées qu'**au tout premier
démarrage** (sinon la contrainte `UNIQUE` sur `numero_compte`
échouerait en réinsérant les mêmes comptes).

**L'accès aux données** (`database.py`) : une connexion SQLite est
ouverte, utilisée, puis fermée à chaque requête HTTP (pas de connexion
partagée entre requêtes). Toutes les requêtes utilisent des paramètres
liés (`?`), jamais de concaténation de texte — élimine le risque
d'injection SQL.

> Bug réel trouvé et corrigé pendant le développement : FastAPI exécute
> certaines requêtes dans un pool de threads, et une connexion SQLite
> ouverte dans un thread ne peut par défaut pas être fermée dans un
> autre. Corrigé avec `check_same_thread=False`. Bon exemple à citer si
> le jury demande "as-tu rencontré des bugs" — ça montre un vrai test en
> conditions réelles, pas juste en local.

## 4. Technologies utilisées

- **SQLite** — moteur de base de données, un seul fichier
  (`fraudshield.db`), aucun serveur à installer
- **module `sqlite3`** — natif de Python, pas d'ORM : requêtes SQL
  écrites directement, avec paramètres liés

## 5. Questions de jury probables

- Pourquoi SQLite et pas PostgreSQL/MySQL ?
- Comment évites-tu l'injection SQL ?
- Que se passe-t-il si deux transactions arrivent en même temps ?
- Pourquoi 3 tables séparées et pas une seule table plate ?
- Que fait la contrainte `CHECK (montant > 0)` ?
- Qu'arrive-t-il si on supprime un compte qui a des transactions ?
- Pourquoi ne pas utiliser un ORM (SQLAlchemy) ?

## 6. Comment répondre simplement

**"Pourquoi SQLite et pas PostgreSQL ?"**
"Pour un prototype qui doit tourner en local sans installation — un
seul fichier, zéro configuration serveur. Testé jusqu'à 30 requêtes
simultanées sans erreur. Pour un vrai volume de production, une
migration vers PostgreSQL serait l'étape suivante, et le code est déjà
isolé dans une seule couche (`transaction_service.py`) pour que ce
changement n'impacte pas le reste de l'application."

**"Injection SQL ?"**
"Toutes les requêtes utilisent des `?` (paramètres liés), jamais de
texte de transaction inséré directement dans la requête SQL — vérifié
sur l'ensemble du code."

**"Deux transactions en même temps ?"**
"Testé réellement avec 30 requêtes envoyées en parallèle : 0 erreur.
SQLite met en file d'attente les écritures concurrentes avec un délai
d'attente par défaut, suffisant pour ce volume."

**"Pourquoi 3 tables et pas une seule ?"**
"Séparer `transactions` (le fait brut) et `analyses_fraude` (le
jugement du modèle) permet de changer de modèle ML sans toucher aux
données historiques, et illustre une relation 1–1 propre plutôt que
d'entasser toutes les colonnes au même endroit."

**"Pourquoi pas un ORM comme SQLAlchemy ?"**
"Pour 3 tables et une poignée de requêtes, le module `sqlite3` natif de
Python suffit et reste simple à expliquer — un ORM aurait ajouté une
couche d'abstraction sans bénéfice réel à cette échelle."

---

## Résumé express (30 secondes, si le temps manque)

"Le module ML génère un dataset synthétique volontairement bruité,
compare 3 modèles avec des métriques mesurées, retient Random Forest
(F1 = 0,80) et l'expose via une fonction unique de prédiction. Le module
base de données stocke comptes, transactions et analyses dans 3 tables
SQLite reliées, avec des contraintes qui garantissent la cohérence — et
c'est cette base qui alimente la feature la plus importante du modèle :
la moyenne historique du compte."
