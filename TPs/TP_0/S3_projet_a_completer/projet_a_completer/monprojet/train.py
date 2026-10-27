"""Entraîne chaque modèle candidat, l'évalue sur le jeu de test et les compare.

Usage, depuis la racine du projet : python -m monprojet.train
"""
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score, f1_score, mean_absolute_error, mean_squared_error,
                             precision_score, r2_score, recall_score)
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from monprojet import config
from monprojet.data import load_data, split
from monprojet.models import candidates
from pathlib import Path

HIGHER_IS_BETTER = {"accuracy": True, "recall": True, "precision": True, "f1": True,
                    "mae": False, "rmse": False, "r2": True}


def build_preprocessing(X: pd.DataFrame) -> ColumnTransformer:
    """Prépare les colonnes : nombres mis à l'échelle, catégories encodées, texte vectorisé. (Fournie.)"""
    text = [config.TEXT_COLUMN] if config.TEXT_COLUMN else []
    numeric = [c for c in X.columns if c not in text and pd.api.types.is_numeric_dtype(X[c])]
    categorical = [c for c in X.columns if c not in text and c not in numeric]
    steps = []
    if numeric:
        steps.append(("nombres", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), numeric))
    if categorical:
        steps.append(("categories", make_pipeline(SimpleImputer(strategy="most_frequent"),
                                                  OneHotEncoder(handle_unknown="ignore")), categorical))
    if text:
        steps.append(("texte", TfidfVectorizer(), config.TEXT_COLUMN))
    return ColumnTransformer(steps, sparse_threshold=0)


def evaluate(model, X_test, y_test) -> dict:
    """Évalue un modèle sur le jeu de test et renvoie les métriques."""

    # 1. Faire les prédictions
    y_pred = model.predict(X_test)

    # 2. Classification
    if config.TASK == "classification":
        # Binaire si la cible contient deux classes, sinon multiclasse
        average = "binary" if y_test.nunique() == 2 else "macro"

        # En classification binaire, sklearn attend généralement la classe positive 1.
        # Si les classes sont différentes de {0, 1}, utiliser macro pour éviter
        # une erreur liée à la valeur de la classe positive.
        if average == "binary" and set(y_test.unique()) != {0, 1}:
            average = "macro"

        scores = {
            "accuracy": accuracy_score(y_test, y_pred),
            "recall": recall_score(
                y_test, y_pred, average=average, zero_division=0
            ),
            "precision": precision_score(
                y_test, y_pred, average=average, zero_division=0
            ),
            "f1": f1_score(
                y_test, y_pred, average=average, zero_division=0
            ),
        }

    # 3. Régression
    elif config.TASK == "regression":
        scores = {
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
        }

    else:
        raise ValueError(
            f"Tâche inconnue : {config.TASK!r}. "
            "Valeurs attendues : 'classification' ou 'regression'."
        )

    # 4. Convertir en float et arrondir à 3 décimales
    return {
        name: round(float(value), 3)
        for name, value in scores.items()
    }



def main() -> None:
    """Entraîne les candidats, compare leurs performances et sauvegarde le meilleur."""

    # 1. Charger et découper les données
    df = load_data()
    X_train, X_test, y_train, y_test = split(df)

    # Les métriques à maximiser ou minimiser
    higher_is_better = config.MAIN_METRIC not in {"mae", "rmse"}

    # 2. Entraîner et évaluer les modèles
    resultats = {}
    modeles_entraines = {}

    for nom, estimateur in candidates().items():
        pipeline = Pipeline([
            ("preparation", build_preprocessing(X_train)),
            ("modele", estimateur),
        ])

        pipeline.fit(X_train, y_train)

        scores = evaluate(pipeline, X_test, y_test)

        if config.MAIN_METRIC not in scores:
            raise ValueError(
                f"La métrique '{config.MAIN_METRIC}' n'est pas fournie "
                f"par evaluate(). Métriques disponibles : {list(scores)}"
            )

        resultats[nom] = scores
        modeles_entraines[nom] = pipeline

    if not resultats:
        raise ValueError("Aucun modèle candidat n'a été fourni.")

    # 3. Afficher le classement des modèles
    tableau = pd.DataFrame(resultats).T
    tableau.index.name = "Modèle"

    tableau = tableau.sort_values(
        by=config.MAIN_METRIC,
        ascending=not higher_is_better,
    )

    print("\n=== Comparaison des modèles ===")
    print(tableau)

    # 4. Sélectionner le meilleur modèle
    meilleur_nom = (
        max if higher_is_better else min
    )(
        resultats,
        key=lambda nom: resultats[nom][config.MAIN_METRIC],
    )

    meilleur_modele = modeles_entraines[meilleur_nom]

    print(f"\nMeilleur modèle : {meilleur_nom}")
    print(f"Métrique principale : {config.MAIN_METRIC}")
    print(f"Score : {resultats[meilleur_nom][config.MAIN_METRIC]}")

    # 5. Sauvegarder le pipeline et les métriques
    models_dir = Path(config.MODELS_DIR)
    models_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(meilleur_modele, models_dir / "model.joblib")

    metrics = {
        "main_metric": config.MAIN_METRIC,
        "best": meilleur_nom,
        "results": resultats,
    }

    with open(
        models_dir / "metrics.json",
        "w",
        encoding="utf-8",
    ) as fichier:
        json.dump(metrics, fichier, ensure_ascii=False, indent=4)

    print(f"\nModèle sauvegardé : {models_dir / 'model.joblib'}")
    print(f"Métriques sauvegardées : {models_dir / 'metrics.json'}")



if __name__ == "__main__":
    main()
