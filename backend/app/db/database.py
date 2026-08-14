"""
FRAUDSHIELD - Connexion et initialisation de la base de donnees.

Ce module NE REDEFINIT PAS le schema : il execute tel quel le fichier
backend/app/db/schema.sql deja cree (etape "Base de donnees" du projet).
schema.sql utilise "CREATE TABLE IF NOT EXISTS", donc le rejouer a
chaque demarrage est sans danger. seed.sql, lui, n'est joue qu'une
seule fois (au tout premier demarrage), sinon les INSERT dupliqueraient
les donnees de demonstration et feraient echouer les contraintes UNIQUE.
"""

import sqlite3
from collections.abc import Generator

from app.core.config import DB_PATH, SCHEMA_PATH, SEED_PATH


def obtenir_connexion_brute() -> sqlite3.Connection:
    """Ouvre une connexion SQLite avec les reglages utilises dans tout le projet."""
    # check_same_thread=False : FastAPI execute les dependances synchrones
    # (comme celle-ci) dans un pool de threads, et peut ouvrir la connexion
    # dans un thread puis la fermer dans un autre. La connexion n'est de
    # toute facon jamais partagee entre deux requetes en meme temps (une
    # connexion par requete, fermee a la fin), donc c'est sans danger ici.
    connexion = sqlite3.connect(DB_PATH, check_same_thread=False)
    connexion.row_factory = sqlite3.Row  # acces aux colonnes par nom (row["montant"])
    connexion.execute("PRAGMA foreign_keys = ON")
    return connexion


def initialiser_base_de_donnees() -> None:
    """
    Cree le fichier de base de donnees et ses tables si necessaire.
    Appelee une fois au demarrage du serveur (voir main.py).
    """
    base_deja_existante = DB_PATH.exists()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connexion = obtenir_connexion_brute()
    try:
        connexion.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

        if not base_deja_existante:
            connexion.executescript(SEED_PATH.read_text(encoding="utf-8"))
            print(f"Base de donnees initialisee avec les donnees de demo -> {DB_PATH}")
        else:
            print(f"Base de donnees existante reutilisee -> {DB_PATH}")

        connexion.commit()
    finally:
        connexion.close()


def obtenir_connexion() -> Generator[sqlite3.Connection, None, None]:
    """
    Dependance FastAPI (Depends(obtenir_connexion)) : fournit une connexion
    par requete HTTP et la ferme automatiquement ensuite.
    """
    connexion = obtenir_connexion_brute()
    try:
        yield connexion
    finally:
        connexion.close()
