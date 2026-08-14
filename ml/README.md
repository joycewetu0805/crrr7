# FRAUDSHIELD - Module Machine Learning

## Installation (Windows / Mac / Linux)

```
python -m venv venv
venv\Scripts\activate        (Windows)
source venv/bin/activate     (Mac/Linux)

pip install -r ml/requirements.txt
```

## Utilisation

Depuis la racine du projet :

```
# 1. Generer le dataset synthetique d'entrainement
python ml/generate_dataset.py

# 2. Entrainer, comparer et sauvegarder le meilleur modele
python ml/train.py

# 3. Tester une prediction sur une transaction d'exemple
python backend/app/ml/predictor.py
```

## Fichiers produits par l'entrainement

| Fichier | Contenu |
|---|---|
| `ml/data/transactions.csv` | Dataset synthetique (genere par `generate_dataset.py`) |
| `ml/reports/comparaison_modeles.csv` | Tableau comparatif des 3 modeles testes |
| `backend/app/ml/model.pkl` | Pipeline sklearn (pretraitement + meilleur modele), pret pour l'inference |
| `backend/app/ml/metrics.json` | Metriques mesurees sur le jeu de test, pour tracabilite |

## Utiliser le modele dans du code

```python
from backend.app.ml.predictor import predire_transaction

resultat = predire_transaction({
    "montant": 1500.0,
    "montant_moyen_compte": 45.0,
    "heure": 3,
    "type_transaction": "virement",
    "canal": "web",
    "pays_transaction": "Nigeria",
    "pays_habituel_compte": "France",
    "nb_transactions_1h": 2,
})
# {"frauduleux": True, "probabilite": 0.96, "niveau_risque": "fraude"}
```
