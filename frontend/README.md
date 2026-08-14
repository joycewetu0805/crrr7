# FRAUDSHIELD - Frontend

Dashboard React (Vite + Tailwind CSS v4) consommant l'API FastAPI du projet.

## Lancer le frontend (Windows / Mac / Linux)

Prérequis : Node.js 18+ et le backend démarré (voir `backend/README.md` ou
le message du chat qui l'accompagne) sur `http://127.0.0.1:8000`.

```
cd frontend
npm install
npm run dev
```

Ouvrir **http://localhost:5173**.

En développement, Vite redirige automatiquement tous les appels
`/api/...` vers le backend (`vite.config.js`) : aucune URL à configurer.

## Build de production

```
npm run build
npm run preview
```

## Structure

```
src/
├── api/client.js              appels HTTP vers l'API FastAPI
├── hooks/useDashboardData.js  chargement + rafraîchissement des données
├── components/
│   ├── layout/                en-tête
│   ├── stats/                 cartes KPI
│   ├── charts/                répartition des risques, montants récents
│   ├── transactions/          tableau, badge de statut, formulaire d'analyse
│   ├── alerts/                bandeau d'alertes de fraude
│   └── common/                icônes, config des statuts, états de chargement
└── pages/Dashboard.jsx        assemble tous les composants
```
