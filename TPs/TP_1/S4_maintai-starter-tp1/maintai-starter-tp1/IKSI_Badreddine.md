# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** IKSI / MAKTABI / ZAHID  
**Date :** 27/10/2026

## 1. Mise en place

**Résultat de `python -m pytest` au début du TP :**

```
3 failed, 10 passed, 1 warning in 3.94s
```

**Quels sont les 4 tests qui passent déjà ?**

Les quatre tests sont :
- `test_health`
- `test_out_of_range_value_is_rejected`
- `test_missing_field_is_rejected`
- `test_openapi_documents_predict`

**Pourquoi les deux tests qui attendent un code 422 passent-ils pour une mauvaise raison ?**

Au début, le schéma `SensorReading` ne contient pas encore les quatre champs nécessaires. Comme `extra="forbid"` interdit les champs inconnus, Pydantic rejette directement les requêtes.

Les tests obtiennent donc bien le code 422 attendu, mais ce n'est pas encore grâce aux bonnes validations.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique |
|---|---|---:|---:|---|
| `temperature_c` | `float` | -40 | 150 | La température peut être négative dans certains cas. Au-delà de 150 °C, elle devient beaucoup trop élevée pour le fonctionnement normal d'un moteur. |
| `vibration_mm_s` | `float` | 0 | 100 | Une vibration ne peut pas être négative. Une valeur de 100 mm/s représente déjà une vibration très importante. |
| `load_pct` | `float` | 0 | 100 | La charge est un pourcentage, donc elle doit rester entre 0 et 100 %. |
| `runtime_hours` | `float` | 0 | 1000000 | Le temps de fonctionnement ne peut pas être négatif. On choisit une limite assez grande pour accepter les machines qui fonctionnent depuis longtemps. |

**Après avoir complété `schemas.py`, quel est le résultat des tests et pourquoi est-ce un bon signe ?**

Les tests indiquent encore trois échecs.

Cela montre que le schéma est maintenant complété, mais que la fonction de prédiction n'est pas encore prête. Les requêtes valides peuvent passer la validation, mais elles échouent ensuite au niveau de l'API.

C'est donc normal à cette étape du TP.

## 3. La fonction `predict()` (`maintai/api/main.py`)

**Code utilisé :**

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

**Pourquoi utiliser le code 503 au lieu de 500 ?**

On utilise le code 503 parce que l'API ne peut pas faire de prédiction lorsque le modèle n'est pas disponible.

Le code 503 indique que le service est indisponible, alors que le code 500 indique plutôt une erreur interne inattendue.

**Pourquoi charger le modèle une seule fois au démarrage ?**

Parce que charger un modèle prend du temps et utilise des ressources.

En le chargeant une seule fois au démarrage, on peut le réutiliser pour toutes les requêtes sans devoir le recharger à chaque fois. Cela rend l'API plus rapide.

## 4. Les tests

**Résultat final de `python -m pytest` :**

```
13 passed, 1 warning in 1.68s
```

Tous les tests passent après avoir complété le schéma et la fonction de prédiction.

## 5. L'API en marche

Après avoir généré les données et entraîné le modèle avec les commandes `python -m maintai.dataset` et `python -m maintai.train`, nous avons démarré l'API avec :

```
uvicorn maintai.api.main:app --reload
```

Ensuite, nous avons testé les différentes requêtes depuis `/docs`.

| Requête | Code obtenu | Réponse |
|---|---|---|
| `GET /health` | 200 | `{"status": "ok", "model_loaded": true}` |
| `POST /v1/predict` avec des valeurs valides | 200 | Une réponse avec la probabilité de panne, l'alerte, le seuil et la version du modèle. |
| `POST /v1/predict` avec une température de 500 °C | 422 | Une erreur indique que la température ne doit pas dépasser 150 °C. |
| `POST /v1/predicte` avec une erreur dans l'adresse | 404 | `{"detail": "Not Found"}` |

**Où peut-on voir les limites des valeurs dans `/docs` ?**

Dans `/docs`, on peut consulter le schéma de la requête `POST /v1/predict`.

On y retrouve les champs demandés, leurs types et les limites minimales et maximales définies dans `schemas.py`.

## 6. Questions de compréhension

**1. Quelle est la différence entre REST et FastAPI ?**

REST est une manière d'organiser une API en utilisant les méthodes HTTP comme GET, POST, PUT et DELETE.

FastAPI est un framework Python qui permet de créer facilement des API en suivant notamment les principes REST.

**2. À quoi sert le schéma Pydantic ?**

Le schéma Pydantic sert à trois choses :

1. Définir les champs et leurs types.
2. Vérifier que les valeurs reçues sont correctes.
3. Aider FastAPI à générer automatiquement la documentation de l'API.

**3. Dans `http://localhost:8000/v1/predict`, que signifient les différentes parties ?**

- `localhost` : c'est notre propre ordinateur sur lequel l'API fonctionne.
- `8000` : c'est le port utilisé par le serveur.
- `/v1/predict` : c'est l'adresse de la fonction qui permet de demander une prédiction.

**4. Pourquoi utilise-t-on `/v1` dans l'adresse ?**

`/v1` signifie qu'il s'agit de la première version de l'API.

Cela permet de créer d'autres versions plus tard, comme `/v2`, sans perturber les applications qui utilisent déjà la première version.

**5. Dans `uvicorn maintai.api.main:app`, que signifient `maintai.api.main` et `app` ?**

`maintai.api.main` représente le fichier Python `maintai/api/main.py` dans lequel se trouve notre API.

`app` est l'objet FastAPI créé dans ce fichier.

Uvicorn utilise cet objet pour démarrer le serveur de l'API.

## 7. Le rendu Git

- **Lien de la pull request :** à compléter.
- **Le tag `tp1` existe sur GitHub :** à vérifier.
- **Personne ayant relu la pull request et commentaire laissé :** à compléter.

## 8. Ce qui reste flou

Pour le moment, nous avons compris les principales étapes du TP et nous n'avons pas de questions particulières.