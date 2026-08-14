"""
FRAUDSHIELD - Entrainement du modele de detection de fraude.

Etapes (dans l'ordre d'execution du script) :
    1. Chargement du dataset
    2. Analyse exploratoire (EDA)
    3. Preparation des features (via ml/features.py)
    4. Separation train / test
    5. Entrainement de plusieurs modeles simples
    6. Comparaison des performances (precision, recall, F1, ROC-AUC, matrice de confusion)
    7. Selection du meilleur modele
    8. Sauvegarde du modele + du rapport de metriques

Lancer avec :  python3 ml/train.py
"""

import json

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from features import (
    COLONNES_BINAIRES,
    COLONNES_CATEGORIELLES,
    COLONNES_NUMERIQUES,
    construire_features,
)

CHEMIN_DONNEES = "ml/data/transactions.csv"
CHEMIN_MODELE = "backend/app/ml/model.pkl"
CHEMIN_METRIQUES = "backend/app/ml/metrics.json"
CHEMIN_COMPARAISON = "ml/reports/comparaison_modeles.csv"


# =====================================================================
# 1. Chargement du dataset
# =====================================================================
print("=" * 70)
print("1. CHARGEMENT DU DATASET")
print("=" * 70)

donnees = pd.read_csv(CHEMIN_DONNEES)
print(f"Dataset charge : {donnees.shape[0]} lignes, {donnees.shape[1]} colonnes")


# =====================================================================
# 2. Analyse exploratoire (EDA)
# =====================================================================
print("\n" + "=" * 70)
print("2. ANALYSE EXPLORATOIRE (EDA)")
print("=" * 70)

print("\n--- Types de colonnes ---")
print(donnees.dtypes)

print("\n--- Valeurs manquantes ---")
manquantes = donnees.isna().sum()
print(manquantes[manquantes > 0] if manquantes.sum() > 0 else "Aucune valeur manquante.")

print("\n--- Equilibre des classes (variable cible : fraude) ---")
repartition = donnees["fraude"].value_counts()
print(repartition)
print(f"Taux de fraude : {donnees['fraude'].mean():.2%}")
print(
    "-> Dataset desequilibre (fraude minoritaire), comme dans la realite.\n"
    "   Consequence directe : l'accuracy seule sera trompeuse (un modele\n"
    "   qui repond toujours 'legitime' aurait deja ~95% d'accuracy sans\n"
    "   detecter une seule fraude). C'est pour cela qu'on juge les modeles\n"
    "   sur precision / recall / F1 / ROC-AUC, pas sur l'accuracy."
)

print("\n--- Statistiques descriptives (montant) ---")
print(donnees.groupby("fraude")["montant"].describe()[["mean", "50%", "min", "max"]])

print("\n--- Repartition heure de nuit (0h-5h) selon la classe ---")
donnees["heure_nuit_tmp"] = donnees["heure"].between(0, 5)
print(donnees.groupby("fraude")["heure_nuit_tmp"].mean().rename("part_transactions_de_nuit"))
donnees.drop(columns="heure_nuit_tmp", inplace=True)

print("\n--- Pays de transaction different du pays habituel, selon la classe ---")
pays_diff = donnees["pays_transaction"] != donnees["pays_habituel_compte"]
print(pays_diff.groupby(donnees["fraude"]).mean().rename("part_pays_inhabituel"))


# =====================================================================
# 3. Preparation des features
# =====================================================================
print("\n" + "=" * 70)
print("3. PREPARATION DES FEATURES")
print("=" * 70)

X = construire_features(donnees)
y = donnees["fraude"]

print(f"Features utilisees ({X.shape[1]}) : {list(X.columns)}")
print("\nApercu des features calculees :")
print(X.head(3))


# =====================================================================
# 4. Separation train / test
# =====================================================================
print("\n" + "=" * 70)
print("4. SEPARATION TRAIN / TEST")
print("=" * 70)

# stratify=y : conserve la meme proportion de fraude dans le train et le
# test. Indispensable ici car la fraude est rare (sinon, un tirage
# malchanceux pourrait donner un jeu de test avec 0 fraude).
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Train : {X_train.shape[0]} transactions ({y_train.mean():.2%} de fraude)")
print(f"Test  : {X_test.shape[0]} transactions ({y_test.mean():.2%} de fraude)")


# =====================================================================
# 5. Entrainement de plusieurs modeles simples
# =====================================================================
print("\n" + "=" * 70)
print("5. ENTRAINEMENT DE PLUSIEURS MODELES")
print("=" * 70)

# Pretraitement commun aux 3 modeles : mis dans un ColumnTransformer pour
# que le meme pipeline serve a l'entrainement ET a l'inference (predictor.py).
pretraitement = ColumnTransformer(transformers=[
    ("num", StandardScaler(), COLONNES_NUMERIQUES),
    ("bin", "passthrough", COLONNES_BINAIRES),
    ("cat", OneHotEncoder(handle_unknown="ignore"), COLONNES_CATEGORIELLES),
])

# class_weight="balanced" : compense le desequilibre des classes en
# donnant plus de poids aux (rares) exemples de fraude pendant
# l'apprentissage, sans avoir a dupliquer/supprimer des lignes.
modeles = {
    "Regression Logistique": LogisticRegression(
        class_weight="balanced", max_iter=1000, random_state=42
    ),
    "Arbre de Decision": DecisionTreeClassifier(
        class_weight="balanced", max_depth=6, random_state=42
    ),
    "Random Forest": RandomForestClassifier(
        class_weight="balanced", n_estimators=200, max_depth=8, random_state=42
    ),
}

pipelines_entraines = {}
for nom, modele in modeles.items():
    pipeline = Pipeline(steps=[("pretraitement", pretraitement), ("modele", modele)])
    pipeline.fit(X_train, y_train)
    pipelines_entraines[nom] = pipeline
    print(f"- {nom} : entraine sur {X_train.shape[0]} transactions")


# =====================================================================
# 6. Comparaison des performances
# =====================================================================
print("\n" + "=" * 70)
print("6. COMPARAISON DES PERFORMANCES (sur le jeu de test, jamais vu)")
print("=" * 70)

resultats = []
for nom, pipeline in pipelines_entraines.items():
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)
    matrice = confusion_matrix(y_test, y_pred)

    resultats.append({
        "modele": nom,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
    })

    print(f"\n--- {nom} ---")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1-score  : {f1:.4f}")
    print(f"ROC-AUC   : {roc_auc:.4f}")
    print("Matrice de confusion [[VN, FP], [FN, VP]] :")
    print(matrice)
    print(classification_report(y_test, y_pred, target_names=["legitime", "fraude"]))

comparaison = pd.DataFrame(resultats).sort_values("f1_score", ascending=False)
print("\n--- Tableau comparatif ---")
print(comparaison.to_string(index=False))

comparaison.to_csv(CHEMIN_COMPARAISON, index=False)
print(f"\nTableau comparatif sauvegarde -> {CHEMIN_COMPARAISON}")


# =====================================================================
# 7. Selection du meilleur modele
# =====================================================================
print("\n" + "=" * 70)
print("7. SELECTION DU MEILLEUR MODELE")
print("=" * 70)

# Critere de selection : le F1-score de la classe "fraude".
# Pourquoi pas l'accuracy ? Parce que le dataset est desequilibre
# (cf. EDA) : l'accuracy resterait haute meme en ratant les fraudes.
# Pourquoi pas seulement le recall ? Parce qu'un modele qui classe TOUT
# en "fraude" aurait un recall parfait mais serait inutilisable (des
# centaines de fausses alertes). Le F1-score est la moyenne harmonique
# de precision et recall : il penalise les deux types d'erreur.
meilleur_nom = comparaison.iloc[0]["modele"]
meilleur_pipeline = pipelines_entraines[meilleur_nom]

print(f"Modele retenu : {meilleur_nom}")
print(f"F1-score : {comparaison.iloc[0]['f1_score']} | ROC-AUC : {comparaison.iloc[0]['roc_auc']}")


# =====================================================================
# 8. Sauvegarde du modele
# =====================================================================
print("\n" + "=" * 70)
print("8. SAUVEGARDE DU MODELE")
print("=" * 70)

joblib.dump(meilleur_pipeline, CHEMIN_MODELE)
print(f"Pipeline (pretraitement + modele) sauvegarde -> {CHEMIN_MODELE}")

metadonnees = {
    "modele_retenu": meilleur_nom,
    "features": list(X.columns),
    "metriques_test": comparaison.iloc[0].to_dict(),
    "comparaison_complete": comparaison.to_dict(orient="records"),
    "taille_train": int(X_train.shape[0]),
    "taille_test": int(X_test.shape[0]),
    "taux_fraude_dataset": round(float(y.mean()), 4),
}
with open(CHEMIN_METRIQUES, "w", encoding="utf-8") as f:
    json.dump(metadonnees, f, indent=2, ensure_ascii=False)
print(f"Rapport de metriques sauvegarde -> {CHEMIN_METRIQUES}")

print("\nEntrainement termine.")
