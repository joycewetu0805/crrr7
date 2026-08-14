"""
FRAUDSHIELD - Routes de l'API.

Couvre les points 3 ("recevoir une transaction") et 9 ("retourner une
reponse JSON claire") de la demande. La validation (point 4) est geree
automatiquement par FastAPI a partir des schemas Pydantic : si le corps
de la requete ne correspond pas a TransactionEntrante, la route n'est
meme pas appelee, une erreur 422 est renvoyee directement.
"""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.db.database import obtenir_connexion
from app.models.schemas import (
    CompteResume,
    ResultatAnalyse,
    Statistiques,
    TransactionEntrante,
    TransactionHistorique,
)
from app.services.transaction_service import (
    CompteInconnuError,
    analyser_et_enregistrer_transaction,
    obtenir_statistiques,
)

router = APIRouter(prefix="/api", tags=["transactions"])


@router.post("/predict", response_model=ResultatAnalyse, status_code=201)
def predire(
    transaction: TransactionEntrante,
    connexion: sqlite3.Connection = Depends(obtenir_connexion),
) -> ResultatAnalyse:
    """
    Recoit une transaction (point 3), la fait analyser par le modele ML
    (points 5-7), l'enregistre en base (point 8) et renvoie le resultat
    complet (point 9).
    """
    try:
        return analyser_et_enregistrer_transaction(connexion, transaction)
    except CompteInconnuError as erreur:
        # 404 : la transaction n'a pas ete enregistree, le compte n'existe pas.
        raise HTTPException(status_code=404, detail=str(erreur))
    except FileNotFoundError as erreur:
        # 503 : le modele ML n'est pas present (ex: clone du depot sans avoir
        # lance ml/train.py). Sans ce bloc, FastAPI renverrait un 500 generique
        # ("Internal Server Error") sans indiquer la cause reelle.
        raise HTTPException(status_code=503, detail=str(erreur))


@router.get("/transactions", response_model=list[TransactionHistorique])
def lister_transactions(
    limite: int = 20,
    connexion: sqlite3.Connection = Depends(obtenir_connexion),
) -> list[dict]:
    """
    Historique des transactions deja analysees, les plus recentes d'abord.
    Sert notamment a VERIFIER que le point 8 (enregistrement) fonctionne
    sans avoir a ouvrir le fichier .db a la main.
    """
    lignes = connexion.execute(
        """
        SELECT
            t.id AS transaction_id,
            c.nom_titulaire AS nom_titulaire,
            t.montant AS montant,
            t.devise AS devise,
            t.type_transaction AS type_transaction,
            t.pays_transaction AS pays_transaction,
            t.date_transaction AS date_transaction,
            a.score_fraude AS probabilite,
            a.statut AS niveau_risque
        FROM transactions t
        JOIN comptes c ON c.id = t.compte_id
        JOIN analyses_fraude a ON a.transaction_id = t.id
        ORDER BY t.date_transaction DESC
        LIMIT ?
        """,
        (limite,),
    ).fetchall()
    # Conversion explicite sqlite3.Row -> dict : garantit que Pydantic
    # peut valider chaque ligne quelle que soit sa version.
    return [dict(ligne) for ligne in lignes]


@router.get("/stats", response_model=Statistiques)
def obtenir_stats(
    connexion: sqlite3.Connection = Depends(obtenir_connexion),
) -> Statistiques:
    """Agregats consommes par les cartes KPI et les graphiques du dashboard."""
    return obtenir_statistiques(connexion)


@router.get("/comptes", response_model=list[CompteResume])
def lister_comptes(
    connexion: sqlite3.Connection = Depends(obtenir_connexion),
) -> list[dict]:
    """Liste des comptes, pour le selecteur du formulaire 'nouvelle transaction'."""
    lignes = connexion.execute(
        "SELECT id, nom_titulaire, pays FROM comptes ORDER BY nom_titulaire"
    ).fetchall()
    return [dict(ligne) for ligne in lignes]
