# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :**MAKTABI/IKSI/ZAHID  ·  **Membres :**MAKTABI SARA  ·  **Date :**27/10/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP1.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
3 failed, 10 passed, 1 warning in 3.94s
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà alors que rien n'est écrit. Lesquels ? Pour les deux tests qui attendent un code 422, expliquez pourquoi ils passent « pour une mauvaise raison » (indice : regardez `extra="forbid"` dans `schemas.py`).

Les 4 tests qui passent sont :
- test_health
- test_out_of_range_value_is_rejected
- test_missing_field_is_rejected
- test_openapi_documents_predict
Les deux tests qui attendent un code 422 sont test_out_of_range_value_is_rejected et test_missing_field_is_rejected.

Ils passent pour une mauvaise raison car, au départ, le schéma SensorReading ne contient pas encore les quatre champs attendus. Avec extra="forbid", Pydantic refuse les champs inconnus. Ainsi, même une requête qui devrait être considérée comme valide est rejetée avec un code 422. Le test passe donc, mais pas pour la bonne raison : il ne vérifie pas réellement les bornes ou les champs obligatoires.
…

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---|---:|---:|---|
| `temperature_c` | `float` | -40 | 150 | Une température moteur peut être négative dans certaines conditions, tandis qu'une température supérieure à 150 °C représente une température extrêmement élevée et anormale. |
| `vibration_mm_s` | `float` | 0 | 100 | Une vibration ne peut pas être négative. Une valeur de 100 mm/s correspond déjà à une vibration très élevée pour une machine industrielle. |
| `load_pct` | `float` | 0 | 100 | La charge est exprimée en pourcentage : elle ne peut pas être négative ni dépasser 100 %. |
| `runtime_hours` | `float` | 0 | 1000000 | Le nombre d'heures de fonctionnement ne peut pas être négatif. Une borne supérieure très élevée permet d'accepter des machines ayant une longue durée de fonctionnement. |

Après avoir écrit `schemas.py` seul, que donne `python -m pytest`, et quel est le message d'erreur des tests qui échouent ? Pourquoi est-ce un bon signe ?

```
3 failed, 10 passed, 1 warning in 3.94s

Les trois tests qui échouent indiquent que la requête reçoit encore un code 422 alors qu'elle devrait atteindre la fonction predict(). C'est un bon signe car cela montre que le schéma accepte désormais les relevés valides et que le problème restant se situe dans l'implémentation de la prédiction.
```

…

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
def predict(reading: SensorReading) -> PredictionOut:

    # Récupérer le modèle chargé
    predictor = state.get("predictor")

    # Vérifier si le modèle est disponible
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle de prédiction non disponible"
        )

    # Effectuer la prédiction
    result = predictor.predict(reading.model_dump())

    return PredictionOut.model_validate(result)
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?

Le code 503 (Service Unavailable) indique que le service est temporairement indisponible car le modèle nécessaire à la prédiction n'est pas disponible. Le problème concerne donc la disponibilité du service et non une erreur interne inattendue. Le code 500 correspondrait plutôt à une erreur interne non prévue.

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?

…Le chargement d'un modèle peut être coûteux en temps et en ressources. Le charger une seule fois au démarrage permet ensuite de le réutiliser pour toutes les requêtes. Cela évite de recharger le modèle à chaque appel et améliore les performances de l'API.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
13 passed, 1 warning in 1.77s
```

## 5. L'API en marche

Après `python -m maintai.dataset` et `python -m maintai.train`, lancez `uvicorn maintai.api.main:app --reload`, puis envoyez ces requêtes depuis `/docs` (ou avec `curl.exe`).

## 5. L'API en marche

Après avoir exécuté `python -m maintai.dataset` et `python -m maintai.train`, j'ai lancé l'API avec `uvicorn maintai.api.main:app --reload`, puis testé les différentes requêtes depuis `/docs`.

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health` | 200 | `{"status": "ok", "model_loaded": true}` |
| `POST /v1/predict` avec `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | 200 | Réponse contenant `failure_probability`, `alert`, `threshold` et `model_version` |
| `POST /v1/predict` avec une température de 500 | 422 | Erreur de validation indiquant que `temperature_c` doit être inférieur ou égal à 150 |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | 404 | `{"detail": "Not Found"}` |

Dans `/docs`, les bornes choisies sont visibles dans la documentation de `POST /v1/predict`, dans le schéma du corps de la requête. Les champs affichent leurs types, leurs descriptions et leurs contraintes de validation, notamment les valeurs minimales et maximales définies avec `ge` et `le` dans `schemas.py`.


…

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?

REST est un style d'architecture qui définit des principes pour concevoir des API, notamment l'utilisation des ressources et des méthodes HTTP comme GET, POST, PUT et DELETE.

FastAPI est un framework Python permettant de développer des API web, notamment des API REST. Il fournit des fonctionnalités comme le routage, la validation avec Pydantic et la génération automatique de la documentation OpenAPI.
   …
2. Le schéma Pydantic sert à trois choses. Lesquelles ?

Le schéma Pydantic sert à :

1. définir la structure et les types des données reçues ;
2. valider les valeurs reçues grâce aux contraintes comme `ge` et `le` ;
3. générer une description exploitable par FastAPI et sa documentation OpenAPI (`/docs`).
   …
3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?

- `localhost` désigne la machine locale sur laquelle l'API est exécutée.
- `8000` est le port sur lequel le serveur Uvicorn écoute les requêtes.
- `/v1/predict` est le chemin de l'endpoint permettant d'envoyer un relevé pour obtenir une prédiction.
   …
4. Pourquoi `/v1` dans l'adresse ?

/v1` indique la version 1 de l'API. Cela permet de faire évoluer l'API ultérieurement sans nécessairement casser les clients qui utilisent une ancienne version. Par exemple, une nouvelle version pourrait être exposée avec `/v2`.
   …
5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?


`maintai.api.main` désigne le module Python contenant l'API. Il correspond au fichier `maintai/api/main.py`.

`app` désigne l'objet FastAPI créé dans ce module avec `app = FastAPI(...)`.

Uvicorn utilise donc cet objet `app` comme application web à démarrer.
   …

## 7. Le rendu Git

- Lien de la pull request : …
- Le tag `tp1` existe sur GitHub : oui / non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  …

## 8. Ce qui reste flou
Aucun point majeur ne reste flou à ce stade.
…
