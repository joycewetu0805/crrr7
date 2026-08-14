"""
FRAUDSHIELD - Schemas Pydantic : validation des donnees entrantes/sortantes.

C'est FastAPI + Pydantic qui assurent le point 4 de la demande
("Valider les donnees recues") : si une requete ne respecte pas ces
regles (montant negatif, type_transaction inconnu...), FastAPI renvoie
automatiquement une erreur 422 AVANT que le code metier ne s'execute.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

# Les valeurs autorisees ici correspondent EXACTEMENT aux contraintes
# CHECK definies dans backend/app/db/schema.sql. Toute incoherence entre
# les deux ferait echouer l'insertion en base avec une erreur peu claire.
TypeTransaction = Literal["achat_en_ligne", "paiement_pos", "retrait_atm", "virement"]
Canal = Literal["web", "mobile", "pos", "atm"]
NiveauRisque = Literal["legitime", "suspect", "fraude"]


class TransactionEntrante(BaseModel):
    """Corps de la requete POST /api/predict : une transaction a analyser."""

    compte_id: int = Field(gt=0, description="Identifiant du compte (table comptes)")
    montant: float = Field(gt=0, description="Montant de la transaction, doit etre positif")
    devise: str = Field(default="EUR", min_length=1, max_length=8)
    type_transaction: TypeTransaction
    canal: Canal
    marchand: Optional[str] = Field(default=None, max_length=255)
    pays_transaction: str = Field(min_length=1, description="Pays ou la transaction a lieu")
    date_transaction: Optional[datetime] = Field(
        default=None,
        description="Date/heure de la transaction. Si absente, l'heure serveur est utilisee.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "compte_id": 1,
                "montant": 1500.0,
                "devise": "EUR",
                "type_transaction": "virement",
                "canal": "web",
                "pays_transaction": "Nigeria",
                "date_transaction": "2026-08-14T03:15:00",
            }
        }
    }


class ResultatAnalyse(BaseModel):
    """Reponse renvoyee au frontend apres analyse (point 9 de la demande)."""

    transaction_id: int
    compte_id: int
    montant: float
    devise: str
    type_transaction: TypeTransaction
    canal: Canal
    pays_transaction: str
    date_transaction: datetime

    frauduleux: bool
    probabilite: float
    niveau_risque: NiveauRisque


class TransactionHistorique(BaseModel):
    """Une ligne de l'historique renvoye par GET /api/transactions."""

    transaction_id: int
    nom_titulaire: str
    montant: float
    devise: str
    type_transaction: TypeTransaction
    pays_transaction: str
    date_transaction: datetime
    probabilite: float
    niveau_risque: NiveauRisque


class CompteResume(BaseModel):
    """Ligne renvoyee par GET /api/comptes, pour peupler le formulaire du frontend."""

    id: int
    nom_titulaire: str
    pays: str


class Statistiques(BaseModel):
    """Agregats renvoyes par GET /api/stats, pour les cartes du dashboard."""

    total_transactions: int
    transactions_analysees: int
    transactions_suspectes: int
    transactions_frauduleuses: int
    taux_fraude: float
    score_risque_moyen: float
