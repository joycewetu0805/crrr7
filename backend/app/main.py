"""
FRAUDSHIELD - Point d'entree du serveur (point 1 de la demande).

Lancer le serveur (depuis le dossier backend/) :
    uvicorn app.main:app --reload

Documentation interactive generee automatiquement (tres utile en demo
devant un jury) : http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import CORS_ORIGINS, TITRE_API, VERSION_API
from app.db.database import initialiser_base_de_donnees

app = FastAPI(title=TITRE_API, version=VERSION_API)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def au_demarrage() -> None:
    """Se connecte a la base et cree les tables si besoin (points 1 et 2)."""
    initialiser_base_de_donnees()


@app.get("/health", tags=["technique"])
def verifier_sante() -> dict:
    """Verification rapide que le serveur repond (utile pour les tests)."""
    return {"status": "ok", "service": TITRE_API}


app.include_router(router)
