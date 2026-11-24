# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :** … · **Membres :** Salma Riad et BOUTAHAR MOHAMED TAHA · **Date :** 24/11/2026

> Les réponses de compréhension et les fichiers de configuration sont complétés. Les sorties de commandes, durées, captures d’écran et lien de pull request doivent être ajoutés après exécution sur le PC, car ils dépendent de votre environnement.

## 1. Mise en place

Sortie de `docker run hello-world` et de `docker version` :

```text
À compléter après installation et démarrage de Docker Desktop.
```

Dernière ligne de `python -m pytest` après la mise en place :

```text
À compléter après exécution. Le polycopié annonce 5 échecs dans tests/test_docker.py et 33 tests réussis avant les modifications Docker.
```

## 2. Image et conteneur

1. **Différence entre image et conteneur :** une image est le paquet figé construit à partir du Dockerfile ; un conteneur est une instance de cette image en cours d’exécution, isolée avec ses propres processus et son réseau.
2. **Pourquoi copier requirements avant maintai ?** Docker peut mettre en cache l’installation des bibliothèques. Si seul le code change, Docker réutilise cette couche et évite de réinstaller les dépendances.
3. **Pourquoi scikit-learn==1.8.0 ?** La version doit être exactement celle utilisée pour entraîner et enregistrer le modèle, afin d’éviter les incompatibilités lors de son chargement.
4. **Pourquoi pas mlflow, dvc et pytest ?** L’image sert l’API et l’interface ; elle n’entraîne pas le modèle et n’exécute pas les tests. Ces outils de développement et de suivi ne sont donc pas nécessaires à l’exécution.

## 3. Sprint 1 : Dockerfile

Le fichier `Dockerfile` du dossier TP6 est complété. Il utilise `python:3.11-slim`, installe les dépendances avant de copier le code, définit les chemins des modèles et données, expose le port 8000 et démarre Uvicorn sur `0.0.0.0`.

| Build | Durée | Taille de l’image (`docker images`) |
|---|---|---|
| Premier build | À mesurer sur le PC | À relever |
| Après modification de `maintai/predict.py` | À mesurer sur le PC | À relever |

**CACHED** signifie que Docker réutilise une couche déjà construite, au lieu de refaire l’étape.

## 4. Sprint 1 : lancer un conteneur

Depuis le dossier `TP6`, après génération du dataset et entraînement du modèle :

```powershell
docker run -d --name maintai-api -p 8000:8000 --env-file .env -v "${PWD}/models:/app/models:ro" maintai:0.4.0
docker ps
docker logs maintai-api
```

| Essai | Réponse attendue à vérifier |
|---|---|
| `GET /health` | HTTP 200 ; le modèle doit être chargé (`model_loaded: true`). |
| `POST /v1/predict` sans clé | HTTP 401 : clé API manquante. |
| `POST /v1/predict` avec la clé de `.env` | Réponse JSON contenant notamment `failure_probability` et le résultat de prédiction. |

**Piège 1 – sans volume du modèle :** le conteneur ne trouve pas les fichiers du modèle. `/health` indique que le modèle n’est pas chargé et la prédiction ne peut pas être effectuée (erreur de service, généralement 503). Le modèle se trouve sur le PC et n’est volontairement pas dans l’image.

**Piège 2 – avec `--host 127.0.0.1` :** Uvicorn écoute uniquement sur l’interface locale du conteneur. Le port publié ne permet donc pas au navigateur du PC d’atteindre l’API ; les logs indiquent une écoute sur `127.0.0.1:8000` et `/health` sur le port 8002 ne répond pas correctement. Il faut écouter sur `0.0.0.0`.

## 5. Sprint 2 : Docker Compose

Le fichier `compose.yaml` définit deux services : `api` expose le port 8000 et monte le modèle en lecture seule ; `ui` lance Streamlit sur le port 8501, monte les données et utilise `http://api:8000` pour joindre l’API sur le réseau Compose.

Sortie de `docker compose ps` :

```text
À coller après docker compose up -d --build.
```

**URL dans la barre latérale :** `http://api:8000`. Elle provient de la variable d’environnement `MAINTAI_API_URL` définie dans `compose.yaml` et lue par `ui/app.py`.

**Pourquoi `api` fonctionne et `localhost` échoue ?** Dans un conteneur, `localhost` désigne ce conteneur lui-même. L’interface et l’API étant dans deux conteneurs distincts, l’interface doit utiliser le nom DNS du service `api` sur le réseau Compose.

Résultats des commandes `docker compose exec ui ...` et dernière ligne de `python -m pytest` :

```text
À coller après exécution. Le polycopié attend 38 passed à la fin du sprint 2.
```

`docker compose down` arrête et supprime les conteneurs et le réseau créés par Compose. Les dossiers de l’hôte montés en volumes, les images et les fichiers locaux ne sont pas supprimés par cette commande.

## 6. Décision : ADR 005

Le modèle et les données ne sont pas intégrés à l’image : ils sont montés au démarrage par des volumes en lecture seule. L’image contient le code et les dépendances, tandis que la clé API est fournie séparément par le fichier `.env`.

## 7. Questions de compréhension

1. **Dans l’image :** système de base, Python, bibliothèques et code (Dockerfile avec `FROM`, `RUN` et `COPY`). **Au lancement :** modèle et données (volumes), clé API (fichier d’environnement), paramètres de démarrage (Compose ou `docker run`).
2. La clé API est un secret. Si elle était copiée dans l’image, toute personne ayant accès à cette image pourrait la récupérer. Elle est donc injectée au lancement avec `--env-file` ou `env_file`.
3. Docker ajoute un environnement d’exécution reproductible : le code, la version de Python et les bibliothèques sont emballés ensemble, puis l’application peut être lancée dans un conteneur sur un autre PC ou serveur équipé de Docker.

## 8. Le rendu Git

- Lien de la pull request : à compléter après création sur GitHub.
- Le tag `tp6` existe sur GitHub : à vérifier après `git push --tags`.
- `git status` avant commit : vérifier que `.env`, `models/`, `data/*.csv` et `mlflow.db` ne sont pas suivis.

Commandes de fin (après validation) :

```bash
docker compose down
git status
git add Dockerfile .dockerignore compose.yaml ui/app.py COMPTE_RENDU.md docs/adr/005-image-docker.md
git commit -m "TP6 : conteneuriser MaintAI avec Docker Compose"
git push
# Après fusion de la pull request :
git switch main
git pull
git tag tp6
git push --tags
```

## 9. Ce qui reste flou

À compléter personnellement après la séance, selon les points qui nécessitent encore des explications.
