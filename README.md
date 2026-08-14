# FraudShield

Plateforme de détection de transactions frauduleuses : une transaction est
envoyée à une API, analysée par un modèle de Machine Learning, et un score
de risque (légitime / suspect / fraude) est renvoyé et affiché sur un
dashboard en temps réel.

## Architecture

```
Frontend (React) → API (FastAPI) → Service de détection → Modèle ML → Base de données (SQLite)
```

## Structure du projet

```
ml/           génération du dataset, entraînement et comparaison des modèles
backend/      API FastAPI (validation, service de détection, base de données)
frontend/     dashboard React (KPI, graphiques, alertes, historique)
docs/         scénario de démo et rapport QA
```

Chaque dossier a son propre `README.md` avec le détail technique.

## Lancer le projet

```
# 1. Backend
cd backend
python -m venv venv && source venv/bin/activate   # venv\Scripts\activate sous Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# 2. Frontend (dans un second terminal)
cd frontend
npm install
npm run dev
```

Dashboard : http://localhost:5173 · API : http://127.0.0.1:8000/docs

Le modèle ML et la base de données sont déjà fournis dans le dépôt
(`backend/app/ml/model.pkl`, `backend/app/db/schema.sql` + `seed.sql`) —
aucune étape d'entraînement n'est nécessaire pour lancer le projet. Pour
regénérer le modèle : voir `ml/README.md`.

## Documentation

- [`docs/DEMO.md`](docs/DEMO.md) — scénario de démonstration (5 minutes) et questions/réponses
- [`docs/QA_REPORT.md`](docs/QA_REPORT.md) — audit qualité et checklist de tests
