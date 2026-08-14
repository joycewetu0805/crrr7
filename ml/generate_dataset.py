"""
FRAUDSHIELD - Generation du dataset d'entrainement.

Pourquoi un dataset synthetique plutot que le dataset Kaggle
"Credit Card Fraud Detection" (celui souvent cite en reference) ?
----------------------------------------------------------------
Le dataset Kaggle est anonymise : ses 28 variables (V1...V28) sont le
resultat d'une transformation PCA, donc illisibles ("V14 = -3.2" ne veut
rien dire pour un jury). Pour un hackathon ou l'on doit EXPLIQUER une
decision (score, facteurs influents), il vaut mieux des variables
metier lisibles (montant, heure, pays...), rattachees au schema de la
base de donnees deja construit (comptes/transactions).

On genere donc ici un dataset synthetique mais realiste : les
transactions frauduleuses ne sont pas etiquetees au hasard, elles
suivent des schemas connus de la detection de fraude (montant
anormalement eleve pour ce compte, pays inhabituel, heure de nuit,
plusieurs transactions rapprochees = "velocity").

Sortie : ml/data/transactions.csv
"""

import numpy as np
import pandas as pd

# Graine fixe : le dataset est reproductible (important pour comparer
# des runs et pour que la demo soit toujours la meme).
RNG = np.random.default_rng(42)

N_COMPTES = 300
N_TRANSACTIONS = 8000

PAYS = ["France", "Belgique", "Allemagne", "Espagne", "Italie"]
PAYS_A_RISQUE = ["Nigeria", "Russie", "Roumanie", "Ukraine"]
TYPES_TRANSACTION = ["achat_en_ligne", "paiement_pos", "retrait_atm", "virement"]
CANAUX = ["web", "mobile", "pos", "atm"]


def generer_comptes(n: int) -> pd.DataFrame:
    """Cree n comptes avec un pays habituel et un niveau de depense propre a chacun."""
    return pd.DataFrame({
        "compte_id": np.arange(1, n + 1),
        "pays_habituel": RNG.choice(PAYS, size=n),
        # Depense moyenne du compte : distribution log-normale =
        # beaucoup de petits montants, quelques comptes "gros depensiers".
        "montant_moyen_compte": RNG.lognormal(mean=3.5, sigma=0.6, size=n).round(2),
    })


def generer_transactions(comptes: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    Genere n transactions reparties sur les comptes, avec un mix normal/fraude.

    Important : les signaux de fraude (montant, pays, heure, velocity) sont
    appliques de facon PROBABILISTE et se chevauchent volontairement avec
    le comportement legitime (un client part parfois en voyage, achete
    parfois cher, ou fait ses courses tard le soir). Un dataset ou la
    fraude serait parfaitement separable du reste ne serait pas realiste
    et donnerait de faux espoirs sur la performance du modele.
    """
    lignes = []

    for _ in range(n):
        compte = comptes.iloc[RNG.integers(0, len(comptes))]
        moyenne = compte["montant_moyen_compte"]

        est_fraude = RNG.random() < 0.05

        type_transaction = RNG.choice(TYPES_TRANSACTION)
        canal = RNG.choice(CANAUX)
        pays_transaction = compte["pays_habituel"]

        # Activite normale = tres peu de transactions rapprochees, avec
        # de rares pics legitimes (ex: courses + plein d'essence coup sur coup).
        nb_transactions_1h = int(RNG.poisson(0.3))
        if RNG.random() < 0.03:
            nb_transactions_1h += int(RNG.poisson(1.5))

        # Heure : la plupart des achats ont lieu en journee/soiree, mais
        # une partie non negligeable de clients legitimes achete la nuit.
        heure = int(RNG.integers(6, 24)) if RNG.random() < 0.85 else int(RNG.integers(0, 6))

        # Montant : bruit multiplicatif autour de l'habitude du compte,
        # avec de rares "gros achats" parfaitement legitimes (electromenager,
        # voyage...).
        if RNG.random() < 0.08:
            montant = moyenne * RNG.uniform(2.5, 6)
        else:
            montant = moyenne * RNG.uniform(0.2, 2.2)

        # Voyage legitime : le pays de transaction differe parfois du pays
        # habituel sans que ce soit une fraude.
        if RNG.random() < 0.05:
            pays_transaction = RNG.choice(PAYS)

        if est_fraude:
            # Chaque signal de fraude est applique avec une probabilite
            # < 1 et peut se cumuler avec le bruit "legitime" ci-dessus :
            # un fraudeur ne coche pas toujours toutes les cases.
            sous_type = RNG.random()
            if sous_type < 0.65:
                # Fraude "classique" : montant nettement plus eleve.
                montant = moyenne * RNG.uniform(2.5, 10) * RNG.uniform(0.7, 1.3)
            else:
                # Fraude "test de carte" : micro-transactions pour valider
                # une carte volee avant une fraude plus importante.
                montant = moyenne * RNG.uniform(0.01, 0.15)
                nb_transactions_1h += int(RNG.integers(1, 5))

            if RNG.random() < 0.55:
                pays_transaction = RNG.choice(PAYS_A_RISQUE)
            if RNG.random() < 0.50:
                heure = int(RNG.integers(0, 6))
            if RNG.random() < 0.35:
                nb_transactions_1h += int(RNG.integers(1, 4))
            if RNG.random() < 0.35:
                type_transaction = RNG.choice(["virement", "retrait_atm"])

        lignes.append({
            "compte_id": int(compte["compte_id"]),
            "montant": round(float(max(montant, 0.5)), 2),
            "montant_moyen_compte": round(float(moyenne), 2),
            "heure": heure,
            "type_transaction": type_transaction,
            "canal": canal,
            "pays_transaction": pays_transaction,
            "pays_habituel_compte": compte["pays_habituel"],
            "nb_transactions_1h": nb_transactions_1h,
            "fraude": int(est_fraude),
        })

    return pd.DataFrame(lignes)


if __name__ == "__main__":
    comptes = generer_comptes(N_COMPTES)
    transactions = generer_transactions(comptes, N_TRANSACTIONS)

    chemin_sortie = "ml/data/transactions.csv"
    transactions.to_csv(chemin_sortie, index=False)

    print(f"{len(transactions)} transactions generees -> {chemin_sortie}")
    print(f"Taux de fraude reel : {transactions['fraude'].mean():.2%}")
