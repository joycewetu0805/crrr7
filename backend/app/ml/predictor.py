"""
FRAUDSHIELD - Inference : notation d'une nouvelle transaction.

Ce module charge UNE FOIS le pipeline sauvegarde par ml/train.py
(pretraitement + modele, dans le meme objet sklearn) et expose une
fonction unique : predire_transaction().

Le pipeline attend exactement les memes colonnes brutes que celles
utilisees a l'entrainement (voir ml/features.py) :
    montant, montant_moyen_compte, heure, type_transaction, canal,
    pays_transaction, pays_habituel_compte, nb_transactions_1h

En pratique, "montant_moyen_compte" et "pays_habituel_compte" sont des
agregats calcules a partir de l'historique du compte en base de donnees
(table `comptes` / historique de `transactions`), pas saisis a la main.
"""

from pathlib import Path

import joblib
import pandas as pd

# ml/features.py est importe pour garantir que l'inference calcule les
# features EXACTEMENT comme a l'entrainement (meme fonction, meme code).
import sys

sys.path.append(str(Path(__file__).resolve().parents[3] / "ml"))
from features import construire_features  # noqa: E402

CHEMIN_MODELE = Path(__file__).resolve().parent / "model.pkl"

# Seuils de decision, coherents avec le statut stocke en base
# (table analyses_fraude.statut : 'legitime' / 'suspect' / 'fraude').
SEUIL_SUSPECT = 0.30
SEUIL_FRAUDE = 0.70

_pipeline = None  # charge paresseusement, une seule fois par processus


def _charger_pipeline():
    global _pipeline
    if _pipeline is None:
        if not CHEMIN_MODELE.exists():
            raise FileNotFoundError(
                f"Modele introuvable : {CHEMIN_MODELE}. "
                "Lancez d'abord 'python3 ml/train.py' pour l'entrainer."
            )
        _pipeline = joblib.load(CHEMIN_MODELE)
    return _pipeline


def _determiner_niveau_risque(probabilite: float) -> str:
    if probabilite >= SEUIL_FRAUDE:
        return "fraude"
    if probabilite >= SEUIL_SUSPECT:
        return "suspect"
    return "legitime"


def predire_transaction(transaction: dict) -> dict:
    """
    Analyse une transaction et retourne la decision du modele.

    Parametres
    ----------
    transaction : dict avec les cles brutes attendues, par exemple :
        {
            "montant": 1500.0,
            "montant_moyen_compte": 45.0,
            "heure": 3,
            "type_transaction": "virement",
            "canal": "web",
            "pays_transaction": "Nigeria",
            "pays_habituel_compte": "France",
            "nb_transactions_1h": 2,
        }

    Retour
    ------
    dict :
        {
            "frauduleux": bool,       # True uniquement si niveau_risque == "fraude"
            "probabilite": float,     # probabilite de fraude estimee par le modele (0-1)
            "niveau_risque": str,     # "legitime" | "suspect" | "fraude"
        }
    """
    pipeline = _charger_pipeline()

    donnees_brutes = pd.DataFrame([transaction])
    features = construire_features(donnees_brutes)

    # predict_proba renvoie [P(classe=0), P(classe=1)] ; on garde P(fraude).
    probabilite = float(pipeline.predict_proba(features)[0, 1])
    niveau_risque = _determiner_niveau_risque(probabilite)

    return {
        "frauduleux": niveau_risque == "fraude",
        "probabilite": round(probabilite, 4),
        "niveau_risque": niveau_risque,
    }


if __name__ == "__main__":
    # Petit test manuel : une transaction clairement suspecte.
    exemple = {
        "montant": 1500.0,
        "montant_moyen_compte": 45.0,
        "heure": 3,
        "type_transaction": "virement",
        "canal": "web",
        "pays_transaction": "Nigeria",
        "pays_habituel_compte": "France",
        "nb_transactions_1h": 2,
    }
    resultat = predire_transaction(exemple)
    print("Transaction :", exemple)
    print("Resultat    :", resultat)
