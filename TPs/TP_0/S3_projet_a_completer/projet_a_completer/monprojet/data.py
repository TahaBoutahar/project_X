
"""Chargement et découpage des données.

À vous d'écrire load_data() et split().
"""
import pandas as pd
from sklearn.model_selection import train_test_split

from monprojet import config


def load_data(path=None) -> pd.DataFrame:
    """Lit le fichier CSV et renvoie un DataFrame.

    Attendu :
    - lire config.DATA_PATH (ou path s'il est donné) ;
    - si la colonne config.TARGET n'existe pas, lever une ValueError avec un message clair ;
    - retirer les lignes où la cible est manquante.

    Pistes : pd.read_csv, df.columns, df.dropna(subset=[...]).
    """
    data_path = path if path is not None else config.DATA_PATH

    df = pd.read_csv(data_path)

    if config.TARGET not in df.columns:
        raise ValueError(
            f"La colonne cible '{config.TARGET}' est absente du fichier CSV."
        )

    df = df.dropna(subset=[config.TARGET])

    return df


def feature_columns(df: pd.DataFrame) -> list:
    """Détermine les colonnes d'entrée."""
    if config.FEATURES is not None:
        return list(config.FEATURES)

    excluded = {config.TARGET, config.TIME_COLUMN}
    return [c for c in df.columns if c not in excluded]


def split(df: pd.DataFrame):
    """Sépare les données en ensembles d'entraînement et de test."""
    X = df[feature_columns(df)]
    y = df[config.TARGET]

    if config.SPLIT == "random":
        # À ajuster selon le type réel de problème (classification ou régression).
        stratify = y if y.nunique() <= 20 else None

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=config.TEST_SIZE,
            random_state=config.SEED,
            stratify=stratify,
        )

    elif config.SPLIT == "chronologique":
        dates = pd.to_datetime(df[config.TIME_COLUMN])
        indices = dates.argsort()

        X = X.iloc[indices]
        y = y.iloc[indices]

        n_test = int(len(df) * config.TEST_SIZE)
        n_train = len(df) - n_test

        X_train = X.iloc[:n_train]
        X_test = X.iloc[n_train:]
        y_train = y.iloc[:n_train]
        y_test = y.iloc[n_train:]

    else:
        raise ValueError(
            f"Valeur de config.SPLIT inconnue : {config.SPLIT!r}"
        )

    return X_train, X_test, y_train, y_test
