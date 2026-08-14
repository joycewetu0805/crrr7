"""
FRAUDSHIELD - Configuration centrale du backend.

Tous les chemins sont calcules a partir de l'emplacement de ce fichier
(Path(__file__)) et non du repertoire courant : le serveur peut donc
etre lance depuis n'importe quel dossier (utile sous Windows, ou le
raccourci/terminal ne demarre pas toujours au meme endroit).
"""

from pathlib import Path

# backend/app/core/config.py -> on remonte de 3 niveaux pour atteindre
# la racine du projet (celle qui contient backend/, ml/, README.md...).
BASE_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = BASE_DIR / "backend"

# Base de donnees SQLite (fichier unique, cf. module base de donnees).
DB_PATH = BACKEND_DIR / "fraudshield.db"

# Scripts SQL deja crees dans le module base de donnees : ce fichier de
# configuration les REFERENCE, il ne les modifie pas.
SCHEMA_PATH = BACKEND_DIR / "app" / "db" / "schema.sql"
SEED_PATH = BACKEND_DIR / "app" / "db" / "seed.sql"

# CORS : ouvert a tous les domaines pour la duree du hackathon, afin que
# le frontend (lance sur un port different, ex: localhost:5173) puisse
# appeler l'API sans configuration supplementaire. A restreindre a un
# domaine precis dans un contexte de production reel.
CORS_ORIGINS = ["*"]

TITRE_API = "FRAUDSHIELD API"
VERSION_API = "1.0.0"
