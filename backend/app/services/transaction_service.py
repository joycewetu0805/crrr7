"""
FRAUDSHIELD - Logique metier : analyser une transaction et l'enregistrer.

Ce fichier concentre les points 5 a 8 de la demande :
    5. Envoyer la transaction au modele Machine Learning
    6. Obtenir la prediction
    7. Calculer/retourner le niveau de risque
    8. Enregistrer la transaction dans la base de donnees

Il reutilise TEL QUEL la fonction predire_transaction() deja creee et
testee dans backend/app/ml/predictor.py (aucune modification de ce
fichier).
"""

import sqlite3
from datetime import datetime

from app.ml.predictor import predire_transaction
from app.models.schemas import ResultatAnalyse, Statistiques, TransactionEntrante

# Format de date utilise partout dans la base (coherent avec
# CURRENT_TIMESTAMP de SQLite : "YYYY-MM-DD HH:MM:SS").
FORMAT_DATE_SQL = "%Y-%m-%d %H:%M:%S"


class CompteInconnuError(Exception):
    """Leve quand le compte_id fourni n'existe pas dans la table comptes."""


def _recuperer_compte(connexion: sqlite3.Connection, compte_id: int) -> sqlite3.Row:
    compte = connexion.execute(
        "SELECT id, pays, statut_compte FROM comptes WHERE id = ?",
        (compte_id,),
    ).fetchone()
    if compte is None:
        raise CompteInconnuError(f"Aucun compte avec l'id {compte_id}")
    return compte


def _calculer_montant_moyen(
    connexion: sqlite3.Connection, compte_id: int, montant_transaction: float
) -> float:
    """Moyenne des montants passes du compte. Sans historique, on retourne
    le montant de la transaction elle-meme (ecart neutre = 1.0) plutot que 0,
    ce qui eviterait une division par zero et fausserait le premier score."""
    resultat = connexion.execute(
        "SELECT AVG(montant) AS moyenne FROM transactions WHERE compte_id = ?",
        (compte_id,),
    ).fetchone()
    moyenne = resultat["moyenne"]
    return float(moyenne) if moyenne is not None else float(montant_transaction)


def _calculer_velocite(
    connexion: sqlite3.Connection, compte_id: int, date_transaction: datetime
) -> int:
    """Nombre de transactions du meme compte dans l'heure precedant celle-ci."""
    date_str = date_transaction.strftime(FORMAT_DATE_SQL)
    resultat = connexion.execute(
        """
        SELECT COUNT(*) AS nb
        FROM transactions
        WHERE compte_id = ?
          AND date_transaction >= datetime(?, '-1 hours')
          AND date_transaction < ?
        """,
        (compte_id, date_str, date_str),
    ).fetchone()
    return int(resultat["nb"])


def _enregistrer_transaction(
    connexion: sqlite3.Connection, transaction: TransactionEntrante, date_transaction: datetime
) -> int:
    curseur = connexion.execute(
        """
        INSERT INTO transactions
            (compte_id, montant, devise, type_transaction, canal,
             marchand, pays_transaction, date_transaction)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            transaction.compte_id,
            transaction.montant,
            transaction.devise,
            transaction.type_transaction,
            transaction.canal,
            transaction.marchand,
            transaction.pays_transaction,
            date_transaction.strftime(FORMAT_DATE_SQL),
        ),
    )
    return curseur.lastrowid


def _enregistrer_analyse(
    connexion: sqlite3.Connection, transaction_id: int, prediction: dict
) -> None:
    connexion.execute(
        """
        INSERT INTO analyses_fraude
            (transaction_id, score_fraude, statut, modele_version)
        VALUES (?, ?, ?, ?)
        """,
        (transaction_id, prediction["probabilite"], prediction["niveau_risque"], "v1"),
    )


def analyser_et_enregistrer_transaction(
    connexion: sqlite3.Connection, transaction: TransactionEntrante
) -> ResultatAnalyse:
    """
    Point d'entree unique utilise par la route POST /api/predict.

    Deroule : verifie le compte -> calcule le contexte (moyenne, velocite)
    -> interroge le modele ML -> enregistre transaction + analyse -> renvoie
    le resultat complet.
    """
    compte = _recuperer_compte(connexion, transaction.compte_id)
    date_transaction = transaction.date_transaction or datetime.now()

    # --- Construction du contexte necessaire au modele (point 5) ---
    montant_moyen_compte = _calculer_montant_moyen(
        connexion, transaction.compte_id, transaction.montant
    )
    nb_transactions_1h = _calculer_velocite(connexion, transaction.compte_id, date_transaction)

    transaction_pour_modele = {
        "montant": transaction.montant,
        "montant_moyen_compte": montant_moyen_compte,
        "heure": date_transaction.hour,
        "type_transaction": transaction.type_transaction,
        "canal": transaction.canal,
        "pays_transaction": transaction.pays_transaction,
        "pays_habituel_compte": compte["pays"],
        "nb_transactions_1h": nb_transactions_1h,
    }

    # --- Prediction (points 6 et 7) ---
    prediction = predire_transaction(transaction_pour_modele)

    # --- Enregistrement en base (point 8) ---
    transaction_id = _enregistrer_transaction(connexion, transaction, date_transaction)
    _enregistrer_analyse(connexion, transaction_id, prediction)
    connexion.commit()

    return ResultatAnalyse(
        transaction_id=transaction_id,
        compte_id=transaction.compte_id,
        montant=transaction.montant,
        devise=transaction.devise,
        type_transaction=transaction.type_transaction,
        canal=transaction.canal,
        pays_transaction=transaction.pays_transaction,
        date_transaction=date_transaction,
        frauduleux=prediction["frauduleux"],
        probabilite=prediction["probabilite"],
        niveau_risque=prediction["niveau_risque"],
    )


def obtenir_statistiques(connexion: sqlite3.Connection) -> Statistiques:
    """Agregats consommes par le dashboard (cartes KPI + graphiques)."""
    ligne = connexion.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM transactions) AS total_transactions,
            (SELECT COUNT(*) FROM analyses_fraude) AS transactions_analysees,
            (SELECT COUNT(*) FROM analyses_fraude WHERE statut = 'suspect') AS transactions_suspectes,
            (SELECT COUNT(*) FROM analyses_fraude WHERE statut = 'fraude') AS transactions_frauduleuses,
            (SELECT COALESCE(AVG(score_fraude), 0) FROM analyses_fraude) AS score_risque_moyen
        """
    ).fetchone()

    total = ligne["total_transactions"]
    frauduleuses = ligne["transactions_frauduleuses"]
    taux_fraude = (frauduleuses / total) if total > 0 else 0.0

    return Statistiques(
        total_transactions=total,
        transactions_analysees=ligne["transactions_analysees"],
        transactions_suspectes=ligne["transactions_suspectes"],
        transactions_frauduleuses=frauduleuses,
        taux_fraude=round(taux_fraude, 4),
        score_risque_moyen=round(float(ligne["score_risque_moyen"]), 4),
    )
