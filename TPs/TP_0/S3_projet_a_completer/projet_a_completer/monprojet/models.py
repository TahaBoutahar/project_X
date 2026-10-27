
from monprojet import config

from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor


def candidates() -> dict:
    """Renvoie les modèles non entraînés à comparer."""

    if config.TASK == "classification":
        return {
            # 1. Baseline : modèle le plus simple
            "Dummy": DummyClassifier(strategy="most_frequent"),

            # 2. Vrais modèles de classification
            "LogisticRegression": LogisticRegression(
                max_iter=1000,
                random_state=config.SEED
            ),
            "RandomForest": RandomForestClassifier(
                n_estimators=100,
                random_state=config.SEED
            ),
            "HistGradientBoosting": HistGradientBoostingClassifier(
                random_state=config.SEED
            ),
            "KNeighbors": KNeighborsClassifier()
        }

    elif config.TASK == "regression":
        return {
            # 1. Baseline : prédiction de la moyenne
            "Dummy": DummyRegressor(strategy="mean"),

            # 2. Vrais modèles de régression
            "Ridge": Ridge(),
            "RandomForest": RandomForestRegressor(
                n_estimators=100,
                random_state=config.SEED
            ),
            "HistGradientBoosting": HistGradientBoostingRegressor(
                random_state=config.SEED
            ),
            "KNeighbors": KNeighborsRegressor()
        }

    else:
        raise ValueError(
            f"Tâche inconnue : {config.TASK!r}. "
            "Valeurs attendues : 'classification' ou 'regression'."
        )
