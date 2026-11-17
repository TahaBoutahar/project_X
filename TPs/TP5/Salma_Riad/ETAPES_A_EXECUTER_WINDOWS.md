# TP5 — Étapes de validation sur Windows — Salma Riad

**Important :** exécuter depuis `TP\TP5` dans le dépôt Git existant du groupe, sur la branche `tp5`. Le ZIP contient le CSV v1 généré ; les données sont exclues de Git. Ne pas déposer TP5 dans un autre dépôt sans adapter le chemin.

## 1. Préparer le projet (PowerShell ou terminal VS Code)

```powershell
cd TP\TP5
# Activer l'environnement existant du TP4 ou créer le vôtre :
# py -3.13 -m venv .venv
# .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
python -m maintai.dataset
python -m pytest
```

**Attendu :** 32 passed. Si Python 3.13 et les versions figées ne s'installent pas, relever le message d'erreur avant toute modification des versions.

## 2. Enregistrer 5 runs MLflow sur la v1

```powershell
python -m maintai.train
python -m maintai.train --C 0.01
python -m maintai.train --threshold 0.2
python -m maintai.train --model forest
python -m maintai.train --threshold 0.3
mlflow ui
```

Ouvrir http://localhost:5000 puis **Model training → maintai → Runs**. Relever identifiants des runs, recall, precision et accuracy et mettre à jour le compte rendu et l'ADR 004. La fenêtre `mlflow ui` doit rester ouverte.

## 3. Initialiser DVC et sauvegarder la v1

Depuis la racine `TP\TP5` (dans un dépôt Git parent déjà initialisé) :

```powershell
dvc init --subdir
git add .dvc .dvcignore
git commit -m "DVC : init"
dvc add data/sensors.csv
git add data/sensors.csv.dvc data/.gitignore
git commit -m "Données v1"
New-Item -ItemType Directory -Force "$env:USERPROFILE\dvc-stockage"
dvc remote add --local -d stockage "$env:USERPROFILE\dvc-stockage"
dvc push
```

Noter le hash Git du commit « Données v1 » :

```powershell
git log --oneline -5
Get-Content data/sensors.csv.dvc
```

## 4. Générer la v2 et la versionner

```powershell
python -m maintai.dataset --n 8000 --seed 7
dvc status
dvc add data/sensors.csv
git add data/sensors.csv.dvc
git commit -m "Données v2"
dvc push
python -m maintai.train
```

## 5. Tester les retours et le téléchargement

Remplacer `HASH_V1` par le hash trouvé dans l'historique Git. Ne pas garder les chevrons.

```powershell
git checkout HASH_V1 -- data/sensors.csv.dvc
dvc checkout
python -c "import pandas as pd; print(len(pd.read_csv('data/sensors.csv')))"
# Attendu : 5000

git checkout HEAD -- data/sensors.csv.dvc
dvc checkout
python -c "import pandas as pd; print(len(pd.read_csv('data/sensors.csv')))"
# Attendu : 8000

Remove-Item data/sensors.csv
Remove-Item -Recurse -Force .dvc/cache
dvc pull
python -c "import pandas as pd; print(len(pd.read_csv('data/sensors.csv')))"
# Attendu : 8000
```

## 6. Rendre le TP5

- Compléter dans `COMPTE_RENDU.md` : sorties réelles, IDs MLflow, hash des commits et lien PR.
- Compléter l'ID du run dans `docs/adr/004-choix-du-modele.md`.
- Ajouter des captures de `32 passed`, de MLflow et des deux versions DVC si demandées par la professeure.

```powershell
git status
git add TP/TP5  # UNIQUEMENT si vous êtes à la racine du dépôt (sinon : git add .)
git commit -m "TP5 : MLflow, DVC, compte rendu et ADR 004"
git push -u origin tp5
```

Créer et fusionner une pull request dans GitHub. **Après fusion**, dans la racine du dépôt :

```powershell
git switch main
git pull
git tag tp5
git push origin tp5
```

**Ne jamais ajouter** `mlflow.db`, `mlruns/`, `data/sensors.csv`, `.dvc/cache/` ou `.dvc/config.local` à Git.
