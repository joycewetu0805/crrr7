# FRAUDSHIELD — Rapport QA & checklist de tests

Audit effectué par lecture de code + tests réels exécutés (pyflakes, py_compile,
oxlint, TestClient FastAPI, requêtes concurrentes, navigateur réel via
Playwright). Rien ci-dessous n'est une supposition non vérifiée.

## 1. Compatibilité inter-modules (Frontend → API → Service → ML → DB)

| Interface | Vérifié | Résultat |
|---|---|---|
| Noms de champs `transactions`/`comptes`/`analyses_fraude` (schema.sql) ↔ Pydantic (schemas.py) | ✅ | Identiques |
| Champs Pydantic (`ResultatAnalyse`, `TransactionHistorique`, `Statistiques`, `CompteResume`) ↔ champs lus côté frontend | ✅ | Identiques (`grep` croisé) |
| Colonnes attendues par `ml/features.py` ↔ dict construit par `transaction_service.py` | ✅ | Identiques |
| Sortie de `predictor.py` (`frauduleux`/`probabilite`/`niveau_risque`) ↔ `ResultatAnalyse` | ✅ | Identiques |

**1 écart fonctionnel trouvé et corrigé** (voir section Corrections).

## 2. Erreurs potentielles / imports

- `python3 -m py_compile` sur tout `backend/app` et `ml` → **0 erreur**.
- `pyflakes` sur `backend/app` et `ml` (imports inutilisés, noms non définis) → **0 signalement**.
- `npm run lint` (oxlint) sur `frontend/src` → **0 signalement**.
- Chemins (`Path(__file__).resolve().parents[...]`) vérifiés dans `config.py` et `predictor.py` : cohérents entre eux, indépendants du répertoire de lancement.

## 3. Connexion API (frontend ↔ backend)

- CORS : `allow_origins=["*"]` → aucune erreur CORS observée en conditions réelles (navigateur, DevTools).
- Proxy Vite (`/api` → `http://127.0.0.1:8000`) testé en mode `npm run dev` **et** `npm run build && npm run preview` → fonctionne dans les deux cas.
- Gestion d'erreur réseau côté frontend : `client.js` lève une erreur lisible, affichée par `EtatErreur` avec l'instruction pour relancer le backend.

## 4. Base de données

- Initialisation idempotente (`CREATE TABLE IF NOT EXISTS` rejoué à chaque démarrage, `seed.sql` uniquement au premier démarrage) → testé par 2 démarrages consécutifs.
- **Test de charge** : 30 requêtes `POST /api/predict` envoyées en parallèle (10 threads) → **0 erreur**, 30/30 réponses `201`. Le verrou SQLite (busy timeout par défaut) absorbe la charge attendue pour une démo.
- Toutes les requêtes SQL utilisent des paramètres `?` (aucune concaténation de chaîne) → pas d'injection SQL possible.
- 1 bug réel trouvé et corrigé (voir Corrections) : connexions SQLite partagées entre threads du pool FastAPI.

## 5. Validation des données

- `montant <= 0`, `type_transaction`/`canal` hors énumération → `422` avec message clair (testé).
- `compte_id` inexistant → `404` (testé).
- Pas de borne haute sur `montant` ni de whitelist stricte sur `devise` : accepté tel quel, sans risque (le modèle ne fait que produire une probabilité, aucun calcul financier réel n'en dépend). **Non corrigé** : hors périmètre du MVP.

## 6. Prédiction ML

- Modèle chargé une seule fois par processus (`_pipeline` mis en cache) → vérifié par inspection.
- Si `model.pkl` est absent (dépôt cloné sans avoir lancé `ml/train.py`) : avant correction, `FileNotFoundError` non interceptée → `500` opaque. **Corrigé** (voir Corrections).
- Limite déjà documentée précédemment : un montant très inférieur à la moyenne habituelle du compte peut ressortir "suspect" (chevauchement avec le pattern "test de carte volée" dans les données d'entraînement). Comportement du modèle, pas un bug.

## 7. Frontend / Backend

- Tous les champs consommés par les composants React existent bien dans les réponses de l'API (vérifié par `grep` croisé, section 1).
- Aucun `dangerouslySetInnerHTML`, `eval`, ni `innerHTML` dans le code → pas de vecteur XSS trouvé.
- **1 écart fonctionnel trouvé et corrigé** : le panneau d'alertes n'affichait que les transactions "fraude", pas "suspect" (voir Corrections).

## 8. Failles évidentes (sécurité)

Constats **assumés pour un MVP de hackathon**, listés pour transparence — non corrigés, car hors scope d'une démo d'une nuit et non demandés explicitement :

| Constat | Risque réel pour la démo | Recommandation si mise en prod |
|---|---|---|
| Aucune authentification sur l'API | Nul (réseau local, pas d'exposition publique) | Ajouter une auth (API key / JWT) |
| CORS ouvert à `*` | Nul en local | Restreindre au domaine du frontend déployé |
| Pas de rate limiting | Nul (1 seul utilisateur en démo) | Ajouter un middleware de limitation |

## 9. CORS

Aucun problème trouvé (voir section 3). Configuration volontairement permissive, documentée comme telle dans `config.py`.

## 10. Variables d'environnement

Le projet n'utilise **aucune variable d'environnement** : tous les chemins sont dérivés de l'emplacement des fichiers (`Path(__file__)`), donc indépendants du répertoire de lancement — comportement voulu et vérifié (fonctionne quel que soit le dossier depuis lequel `uvicorn`/`npm` sont lancés). Rien n'est donc "mal configuré" au sens propre : il n'y a rien à configurer. Point relevé pour information, pas un défaut.

---

## Corrections appliquées

Voir le message de réponse principal pour le détail (fichier / ancienne logique / nouvelle logique / raison / comment vérifier) :

1. `backend/app/db/database.py` — connexions SQLite thread-safe (`check_same_thread=False`).
   *Déjà corrigé lors de la construction du dashboard (trouvé en testant dans un vrai
   navigateur) — listé ici pour mémoire, pas une nouvelle correction de cette passe QA.*
2. `frontend/src/components/alerts/FraudAlerts.jsx` — alertes étendues aux transactions "suspect".
   *Nouvelle correction de cette passe.*
3. `backend/app/api/routes.py` — erreur `503` claire si le modèle ML est absent.
   *Nouvelle correction de cette passe.*

---

## Checklist de tests (fonctionnement complet)

### Démarrage
- [ ] `cd backend && uvicorn app.main:app --reload` démarre sans erreur, log `Base de donnees initialisee...`
- [ ] `GET http://127.0.0.1:8000/health` → `200 {"status":"ok"}`
- [ ] `GET http://127.0.0.1:8000/docs` → Swagger s'affiche
- [ ] `cd frontend && npm run dev` démarre sans erreur
- [ ] `http://localhost:5173` affiche le dashboard sans erreur console

### Chemin nominal (transaction légitime)
- [ ] Soumettre une transaction petit montant / pays habituel / heure de jour via le formulaire
- [ ] Le badge affiché est **Légitime** (vert), probabilité basse
- [ ] Le total de transactions s'incrémente, la ligne apparaît en tête du tableau

### Chemin fraude
- [ ] Soumettre une transaction gros montant / pays à risque (Nigeria, Russie...) / heure de nuit
- [ ] Le badge affiché est **Fraude** (rouge), probabilité haute
- [ ] La transaction apparaît dans le panneau "Alertes de risque"
- [ ] Les cartes KPI (frauduleuses, taux de fraude) se mettent à jour

### Chemin suspect
- [ ] Soumettre une transaction avec un seul signal ambigu (ex: retrait DAB nocturne, montant modéré)
- [ ] Le badge affiché est **Suspect** (orange)
- [ ] La transaction apparaît dans "Alertes de risque" avec la couleur orange (pas rouge)

### Validation
- [ ] Montant négatif ou nul → `422`, message clair, formulaire affiche l'erreur
- [ ] `compte_id` inexistant (test via `/docs`) → `404`
- [ ] Champ `type_transaction` invalide → `422`

### Persistance
- [ ] Après une analyse, `GET /api/transactions` contient bien la nouvelle ligne
- [ ] Redémarrer le backend : les données restent (fichier `fraudshield.db` conservé)
- [ ] Supprimer `fraudshield.db` et relancer : la base est recréée avec les données de démo (`seed.sql`)

### Résilience
- [ ] Couper le backend, recharger le frontend → message d'erreur clair + bouton "Réessayer"
- [ ] Relancer le backend, cliquer "Réessayer" → dashboard revient

### Responsive
- [ ] Réduire la fenêtre à une largeur mobile (~390px) → cartes KPI en grille 2 colonnes, tableau scrollable horizontalement, tout reste lisible
