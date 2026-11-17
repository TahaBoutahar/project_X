# COMPTE RENDU — TP5 : MLflow et DVC

**Étudiante : Salma Riad**  
**Module : Développement et déploiement d’applications intelligentes — Séance 7**  
**Projet : MaintAI**  
**Date : 17 novembre 2026**

> **État de validation :** la fonction demandée est implémentée et les données v1 sont générées. Les valeurs de métriques ci-dessous ont été **calculées localement avec scikit-learn**, et non récupérées de MLflow. MLflow et DVC ne sont pas installés dans l'environnement de préparation, donc les 32 tests, les identifiants des runs, les commits DVC et la pull request restent à vérifier sur le PC de l'étudiante. Ne pas présenter ces opérations comme réalisées.

## 1. Mise en place

- Starter TP5 dans `TP/TP5` ; package MaintAI version 0.3.0.
- Installation : `python -m pip install -r requirements.txt` puis `python -m pip install -e .`.
- Tests initiaux attendus avec le starter non complété : **5 failed, 27 passed** (les cinq tests de suivi MLflow échouent car `log_run` n'enregistre aucun run).
- Après correction de `tracking.py`, résultat attendu : **32 passed** ; **à confirmer** avec `python -m pytest`.
- `pip install -e .` relie l'import `maintai` au code source de TP5 plutôt qu'à l'installation précédente de TP4.

## 2. Sprint 1 — MLflow

### Implémentation de `log_run`

```python
def log_run(params: dict, metrics: dict, model, X_example, data_path: Path) -> str:
    """Enregistre un entraînement : paramètres, version des données, métriques et modèle. Renvoie l'id du run."""
    mlflow.set_experiment(EXPERIMENT)
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_param("data_md5", file_md5(data_path))
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(
            model,
            name="model",
            input_example=X_example,
            skops_trusted_types=TRUSTED_TYPES,
        )
        return run.info.run_id

```

La fonction choisit l'expérience `maintai`, ouvre un run, enregistre les paramètres et `data_md5`, les métriques, le modèle sklearn avec `skops_trusted_types=TRUSTED_TYPES` et renvoie l'identifiant du run.

### Résultats calculés localement sur les données v1 (5000 relevés)

| Commande | Recall | Precision | Accuracy | Run MLflow |
|---|---:|---:|---:|---|
| `python -m maintai.train` | 0.574 | 0.736 | 0.914 | À relever |
| `python -m maintai.train --C 0.01` | 0.397 | 0.885 | 0.911 | À relever |
| `python -m maintai.train --threshold 0.2` | 0.838 | 0.543 | 0.882 | À relever |
| `python -m maintai.train --model forest` | 0.544 | 0.679 | 0.903 | À relever |
| `python -m maintai.train --threshold 0.3` | 0.75 | 0.622 | 0.904 | À relever |

**Interprétation :** une panne manquée coûte plus cher qu'une fausse alerte. On privilégie donc le rappel (`recall`), puis on examine la précision pour quantifier les fausses alertes. Un seuil plus bas peut augmenter le rappel au prix d'une baisse de la précision. La forêt aléatoire ne doit pas être déclarée supérieure sans comparer ses métriques.

**Version de scikit-learn :** les dépendances fournies fixent `scikit-learn==1.8.0`. La version **réellement inscrite** dans le `requirements.txt` de l'artefact MLflow reste à contrôler dans l'interface après exécution. Cela améliore la reproductibilité et évite un écart entre versions lors du chargement du modèle.

**Où sont les runs ?** Les runs MLflow sont stockés localement dans `mlflow.db` et les artefacts associés (par exemple `mlruns/` selon la configuration). Ces fichiers sont exclus de Git : ce sont des artefacts d'exécution, pas du code source.

## 3. Sprint 2 — DVC

**v1 :** 5000 relevés, MD5 du fichier CSV = `b7fec4274774842dc1f48202c6013490`.  
**v2 :** 8000 relevés, MD5 du fichier CSV = `31ef5ebb63ef2331a31dfe009ef8796a`.

Ces MD5 ont été calculés sur les CSV générés à partir du code du starter. Le champ DVC `md5` n'est pas encore créé : il le sera avec `dvc add data/sensors.csv`.

**Comparaison `data_md5` / DVC :** les deux empreintes doivent être identiques pour un même fichier. Ainsi, on peut retrouver précisément les données correspondant à chaque run.

**Pourquoi ne pas versionner directement le CSV dans Git ?** Git versionne le petit fichier `data/sensors.csv.dvc` (empreinte + taille + chemin), tandis que DVC conserve les données lourdes dans son cache et dans le stockage distant.

Après génération de la v2, `dvc status` doit signaler que `data/sensors.csv` a changé par rapport à son reçu v1.

| Version | Commit Git | MD5 (8 premiers caractères) | Lignes |
|---|---|---|---:|
| v1 | À relever après commit « Données v1 » | `b7fec427` | 5000 |
| v2 | À relever après commit « Données v2 » | `31ef5ebb` | 8000 |

**Retour v1 et v2 :** restaurer le reçu `.dvc` avec `git checkout <commit-v1> -- data/sensors.csv.dvc`, puis `dvc checkout` ; il faut retrouver **5000 lignes**. Restaurer `HEAD` et relancer `dvc checkout` pour retrouver **8000 lignes**.

**`dvc pull` :** après suppression du CSV et du cache local, DVC récupère la version indiquée par le reçu depuis le stockage configuré, puis restaure le fichier (à vérifier à l'exécution).

## 4. Relier le modèle à ses données

Comparaison locale des réglages standards sur les deux versions :

| Version | data_md5 (8 caractères) | n_train | Recall | Precision |
|---|---|---:|---:|---:|
| v1 | `b7fec427` | 4000 | 0.574 | 0.736 |
| v2 | `31ef5ebb` | 6400 | 0.58 | 0.773 |

Ces résultats décrivent deux jeux de données synthétiques distincts. Une métrique plus élevée ne prouve pas, à elle seule, qu'un modèle est meilleur : les échantillons évalués peuvent être différents. Une conclusion solide demande un jeu de test fixe ou une évaluation comparable.

## 5. Décision — ADR 004

Voir `docs/adr/004-choix-du-modele.md`. L'identifiant d'un run enregistré dans MLflow est indispensable pour finaliser et valider le choix.

## 6. Questions de compréhension

1. **Git** suit le code et les reçus `.dvc`, **DVC** suit les versions de données, **MLflow** trace les paramètres, métriques, modèles et leur provenance.
2. `--local` empêche le chemin spécifique au PC de se retrouver dans Git. Pour partager les données, il faut configurer un stockage commun accessible à l'équipe (S3, serveur ou équivalent).
3. Pour livrer un modèle reproductible, on fournit **le code** (Git + package), **les données** (DVC) et **le modèle avec ses paramètres, métriques et dépendances** (MLflow).

## 7. Le rendu Git (à effectuer)

- Pull request : **à créer**.
- Tag `tp5` : **à créer après fusion**.
- Vérifier avec `git status` que `mlflow.db`, `mlruns/`, `data/sensors.csv`, `.dvc/cache` et `.dvc/config.local` sont exclus.
- Vérifier que les 32 tests passent et qu'au moins 5 runs figurent dans MLflow.

## 8. Ce qui reste flou / à vérifier

Vérifier sur le poste de l'étudiante le fonctionnement de MLflow, le stockage distant local de DVC, le `dvc pull` et la pull request. La distinction importante est entre un run MLflow (trace du modèle) et un reçu DVC (version des données).
