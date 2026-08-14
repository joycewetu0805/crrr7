# FRAUDSHIELD — Scénario de démo (5 minutes) + Q&A jury

## Avant de commencer

- Backend lancé (`uvicorn app.main:app --reload`) et testé (`/health` répond).
- Frontend lancé (`npm run dev`), dashboard ouvert en plein écran.
- Base de données fraîche ou avec les données de démo (`seed.sql`) — évite d'avoir
  un historique déjà saturé d'alertes qui noierait la démo.
- Onglet `/docs` (Swagger) ouvert dans un second onglet, au cas où le jury
  demande à voir l'API directement.

## Déroulé (≈5 min)

| # | Étape | Durée | Ce que vous dites / faites |
|---|---|---|---|
| 1 | Le problème | 0:30 | "La fraude par carte bancaire coûte des milliards chaque année. Les règles fixes ('bloquer si > 1000€') sont rigides et faciles à contourner. Il faut un système qui apprend des comportements." |
| 2 | FraudShield | 0:30 | "FraudShield reçoit une transaction, la compare à l'historique du compte, et un modèle de Machine Learning calcule un score de risque en temps réel — légitime, suspect ou fraude." Montrer le dashboard vide/prêt. |
| 3 | Transaction normale | 0:30 | Remplir le formulaire : compte existant, petit montant (~40€), pays habituel, type "achat en ligne". Cliquer "Analyser". |
| 4 | Analyse par le modèle | 0:15 | Le résultat s'affiche instantanément sous le formulaire. "Le modèle vient de comparer cette transaction à l'historique du compte : montant cohérent, pays habituel, heure normale." |
| 5 | Score de risque | 0:15 | Pointer le badge **Légitime** + le pourcentage affiché (ex: 1-2%). "Une probabilité de fraude très faible." |
| 6 | Transaction suspecte | 0:30 | Remplir à nouveau : même compte, gros montant (3000-5000€), pays à risque (Nigeria/Russie), type "virement". Cliquer "Analyser". |
| 7 | Détection | 0:15 | Le badge passe à **Fraude** (rouge), probabilité élevée (>90%). "Le modèle a détecté 3 signaux combinés : montant hors norme pour ce compte, pays inhabituel, type de transaction à risque." |
| 8 | Alerte | 0:15 | Faire défiler jusqu'au panneau "Alertes de risque" : la transaction vient d'apparaître en tête, en rouge. |
| 9 | Dashboard mis à jour | 0:30 | Montrer les cartes KPI qui se sont incrémentées en direct (total, frauduleuses, taux de fraude), le graphique de répartition, et la ligne dans le tableau d'historique. "Tout se met à jour automatiquement, sans recharger la page." |
| 10 | Valeur ajoutée de l'IA | 1:00 | "Une règle fixe aurait bloqué ou laissé passer selon un seuil unique. Ici, le modèle croise 8 signaux (montant relatif au compte, pays, heure, vélocité, type de transaction...) et sort une probabilité continue, pas juste oui/non — ce qui permet de prioriser : bloquer les cas critiques, mettre en revue manuelle les cas 'suspect', laisser passer le reste sans friction pour le client légitime." |

Reste ~1 min de marge pour les questions.

## Questions difficiles du jury — et vos réponses

**"Votre dataset est synthétique. Comment savoir que ça marche sur de vraies données ?"**
> "Le dataset Kaggle de référence existe (Credit Card Fraud Detection) mais ses variables sont anonymisées par PCA — inexploitables pour expliquer une décision à un client ou un jury. J'ai généré un dataset synthétique avec des règles de fraude probabilistes, volontairement bruitées pour ne pas être parfaitement séparables — ce n'est pas un raccourci de facilité, c'est un choix pour garder un modèle explicable. Sur de vraies données, la même architecture (mêmes features, même pipeline) serait ré-entraînée sans changer une ligne de code applicatif."

**"70% de précision, ça veut dire 30% de fausses alertes. N'est-ce pas trop ?"**
> "C'est un vrai compromis, assumé et mesuré : je privilégie le recall (95% des fraudes détectées) parce que rater une fraude coûte bien plus cher qu'une alerte à vérifier manuellement. Les 30% de faux positifs partent en revue humaine, pas en blocage automatique — c'est le rôle du niveau 'suspect'."

**"Pourquoi Random Forest et pas un réseau de neurones ?"**
> "Sur ~8000 transactions et 9 features, un deep learning n'apporterait rien — il a besoin de bien plus de données et serait moins interprétable. Random Forest donne de la feature importance exploitable, s'entraîne en secondes, et j'ai comparé 3 modèles avec des métriques mesurées avant de choisir, pas au hasard."

**"Comment gérez-vous les fraudes jamais vues auparavant (nouveau pattern) ?"**
> "Honnêtement, un modèle supervisé comme celui-ci apprend des patterns qu'il a vus à l'entraînement — un pattern totalement inédit ne sera pas forcément détecté. C'est une limite connue, qui justifierait un ré-entraînement régulier sur des données fraîches, et éventuellement un modèle complémentaire de détection d'anomalies (non supervisé) en production."

**"SQLite, ça tient la charge en production ?"**
> "Pour ce MVP, oui — j'ai testé 30 requêtes simultanées sans erreur. En production avec un vrai volume de transactions, on migrerait vers PostgreSQL : le code utilise déjà une couche d'accès isolée (`transaction_service.py`), donc ce changement n'impacterait pas le reste de l'application."

**"Il n'y a pas d'authentification sur votre API ?"**
> "Correct, assumé pour la démo — c'est documenté comme limitation connue. Pour une mise en production, j'ajouterais une authentification (clé API ou JWT) et je restreindrais le CORS au domaine du frontend."

**"Le RGPD, vous stockez des données personnelles ?"**
> "Le nom du titulaire et le pays sont stockés, oui. En production, il faudrait un plan de rétention des données, un chiffrement au repos, et une base légale claire (intérêt légitime pour la prévention de la fraude) — hors scope du MVP mais une vraie question à traiter avant un déploiement réel."

**"Pourquoi les seuils 30%/70% et pas d'autres valeurs ?"**
> "Ce sont des seuils de départ raisonnables pour distinguer 3 niveaux d'action (laisser passer / vérifier / bloquer). Ils seraient affinés avec de vraies données de coût métier (coût d'une fraude non détectée vs coût d'une vérification manuelle) — actuellement fixés arbitrairement mais faciles à ajuster (une seule constante dans le code)."

**"Un fraudeur ne pourrait-il pas s'adapter pour passer sous le radar ?"**
> "Oui, c'est une réalité en détection de fraude — j'ai d'ailleurs trouvé ce cas en testant : un très petit montant, en dessous de l'habitude du compte, chevauche le pattern 'test de carte volée' et peut remonter en 'suspect' au lieu de 'légitime'. C'est documenté comme limitation, pas caché. En production, ça se traite avec un ré-entraînement régulier et des features supplémentaires (empreinte device, vitesse de frappe, etc.)."

**"Quelle est la latence d'une prédiction ?"**
> "Le modèle est chargé une seule fois en mémoire au démarrage du serveur — la prédiction elle-même prend quelques millisecondes, le temps de réponse perçu vient surtout de la requête HTTP, pas du calcul ML."
