# FRAUDSHIELD - Backend

API FastAPI : reçoit une transaction, l'envoie au modèle ML, enregistre
le résultat en base SQLite, et expose les données consommées par le
frontend (stats, historique, comptes).

## Lancer le backend (Windows / Mac / Linux)

```
cd backend
python -m venv venv
venv\Scripts\activate        (Windows)
source venv/bin/activate     (Mac/Linux)

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Documentation interactive : **http://127.0.0.1:8000/docs**

Au premier démarrage, `backend/fraudshield.db` est créé automatiquement
à partir de `app/db/schema.sql` et peuplé avec `app/db/seed.sql`.

## Endpoints

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/health` | Vérifie que le serveur répond |
| POST | `/api/predict` | Analyse une transaction (ML) et l'enregistre |
| GET | `/api/transactions?limite=N` | Historique des transactions analysées |
| GET | `/api/stats` | Agrégats pour les cartes KPI du dashboard |
| GET | `/api/comptes` | Liste des comptes (pour le formulaire) |
