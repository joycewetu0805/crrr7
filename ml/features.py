"""
FRAUDSHIELD - Ingenierie des features.

Ce module est partage entre l'entrainement (ml/train.py) et l'inference
(backend/app/ml/predictor.py). C'est volontaire et important : le modele
doit voir EXACTEMENT les memes calculs de features au moment ou il
apprend et au moment ou il predit. Dupliquer cette logique dans deux
fichiers differents est une source classique de bugs difficiles a
detecter en ML ("training/serving skew").

Variables brutes attendues en entree (une ligne = une transaction) :
    montant                 montant de la transaction (EUR)
    montant_moyen_compte    depense moyenne habituelle de ce compte
    heure                   heure de la transaction (0-23)
    type_transaction        achat_en_ligne / paiement_pos / retrait_atm / virement
    canal                   web / mobile / pos / atm
    pays_transaction        pays ou la transaction a lieu
    pays_habituel_compte    pays habituel du titulaire du compte
    nb_transactions_1h      nombre de transactions du meme compte dans l'heure precedente
"""

import pandas as pd

# Colonnes numeriques envoyees telles quelles au modele.
COLONNES_NUMERIQUES = [
    "montant",
    "montant_moyen_compte",
    "ecart_montant",
    "heure",
    "nb_transactions_1h",
]

# Colonnes binaires (0/1), deja numeriques mais issues d'une regle metier.
COLONNES_BINAIRES = [
    "pays_inhabituel",
    "heure_nuit",
]

# Colonnes categorielles, encodees en one-hot par le pipeline sklearn.
COLONNES_CATEGORIELLES = [
    "type_transaction",
    "canal",
]

TOUTES_LES_FEATURES = COLONNES_NUMERIQUES + COLONNES_BINAIRES + COLONNES_CATEGORIELLES

# Heures considerees comme "nuit" : la fraude est statistiquement plus
# frequente sur ce creneau (compte endormi = moins de vigilance/reactivite).
HEURES_NUIT = range(0, 6)


def construire_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme des transactions brutes en features exploitables par le modele.

    Ne fait AUCUN entrainement ni scaling : uniquement des calculs
    deterministes (ratios, indicateurs binaires) identiques a l'entrainement
    et a l'inference.
    """
    df = df.copy()

    # Ecart entre le montant de la transaction et l'habitude du compte.
    # > 1 = le client depense plus que d'habitude ; tres > 1 = suspect.
    df["ecart_montant"] = df["montant"] / df["montant_moyen_compte"].replace(0, 1)

    # Le pays de la transaction differe-t-il du pays habituel du compte ?
    df["pays_inhabituel"] = (
        df["pays_transaction"] != df["pays_habituel_compte"]
    ).astype(int)

    # Transaction effectuee de nuit ?
    df["heure_nuit"] = df["heure"].isin(HEURES_NUIT).astype(int)

    return df[TOUTES_LES_FEATURES]
