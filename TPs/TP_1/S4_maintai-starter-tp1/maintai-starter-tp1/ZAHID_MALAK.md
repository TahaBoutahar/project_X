# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** 1  ·  **Membres :** Zahid Malak  ·  **Date :** 27/10/2026

## 1. Mise en place

Après l'installation, avant d'implémenter le schéma et la fonction `predict`, la
dernière ligne obtenue avec `python -m pytest` était :

```text
3 failed, 10 passed, 1 warning in 19.32s
```

Les quatre tests de `tests/test_api.py` qui passent déjà sont :

- `test_health` ;
- `test_out_of_range_value_is_rejected` ;
- `test_missing_field_is_rejected` ;
- `test_openapi_documents_predict`.

Les tests de valeur hors limite et de champ manquant passent toutefois pour une
mauvaise raison. Comme `SensorReading` ne déclarait encore aucun champ et que
`extra="forbid"` refusait tous les champs reçus, FastAPI renvoyait bien `422`,
mais sans vérifier les bornes ni le champ obligatoire attendu.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique |
|---|---|---:|---:|---|
| `temperature_c` | `float` | `-40` | `150` | Plage réaliste pour un capteur de température industriel. |
| `vibration_mm_s` | `float` | `0` | `50` | Une vibration est positive ; 50 mm/s est une limite haute d'alerte/capteur. |
| `load_pct` | `float` | `0` | `100` | La charge est exprimée en pourcentage de la capacité nominale. |
| `runtime_hours` | `float` | `0` | `200000` | Une durée de fonctionnement ne peut pas être négative ; la limite couvre une longue durée de vie industrielle. |

Après l'écriture de `schemas.py`, les tests qui dépendaient du comportement de
prédiction échouaient avec `NotImplementedError` (ou avec un statut HTTP
inattendu), car la route n'était pas encore implémentée. C'était un bon signe :
les champs étaient désormais réellement validés et les tests atteignaient la
logique de la route au lieu d'être rejetés systématiquement par
`extra="forbid"`.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Corps de la fonction :

```python
predictor = state.get("predictor")
if predictor is None:
    raise HTTPException(status_code=503, detail="Model is not loaded")
return PredictionOut(**predictor.predict(reading.model_dump()))
```

Le code `503 Service Unavailable` indique que le serveur fonctionne mais que le
service ne peut pas encore traiter cette requête, car son modèle est absent.
Un code `500` indiquerait plutôt une erreur interne inattendue du serveur.

Le modèle est chargé une seule fois au démarrage dans la fonction `lifespan`.
Cela évite de relire le fichier du modèle et de réinitialiser le prédicteur à
chaque requête. Les requêtes sont donc plus rapides et utilisent la même
configuration pendant toute la durée de vie du processus.

## 4. Les tests

Après l'implémentation du schéma et de `predict`, la dernière ligne de
`python -m pytest` était :

```text
13 passed, 1 warning in 4.58s
```

L'avertissement concerne la dépréciation de l'utilisation de `httpx` par la
version installée de Starlette ; il ne fait échouer aucun test.

## 5. L'API en marche

Après `python -m maintai.dataset` et `python -m maintai.train`, les réponses
obtenues avec le modèle entraîné étaient :

| Requête | Code obtenu | Réponse (corps JSON) |
|---|---:|---|
| `GET /health` | `200` | `{"status": "ok", "model_loaded": true}` |
| `POST /v1/predict` avec le relevé fourni | `200` | `{"failure_probability": 0.9553, "alert": true, "threshold": 0.3, "model_version": "2026-10-27T18:07:50Z"}` |
| `POST /v1/predict` avec `temperature_c: 500` | `422` | Erreur Pydantic : `temperature_c` doit être inférieur ou égal à `150`. |
| `POST /v1/predicte` | `404` | `{"detail": "Not Found"}` |

La réponse `200` observée dans Swagger est :

```json
{
  "failure_probability": 0.9553,
  "alert": true,
  "threshold": 0.3,
  "model_version": "2026-10-27T18:07:50Z"
}
```

La valeur `model_version` dépend de la date à laquelle le modèle a été entraîné
et peut donc être différente lors d'une nouvelle exécution.

Dans `/docs`, les bornes sont visibles dans le schéma de la requête
`SensorReading`, dans la description de `POST /v1/predict`, ainsi que dans le
schéma OpenAPI généré.

## 6. Questions de compréhension

1. **REST et FastAPI : quelle est la différence ?**  
   REST est un style d'architecture et un ensemble de conventions pour
   concevoir des services HTTP. FastAPI est un framework Python qui permet de
   créer une API, notamment une API respectant ces conventions.

2. **Le schéma Pydantic sert à trois choses.**  
   Il décrit la structure des données, valide les types et les contraintes
   (bornes, champs obligatoires, champs inconnus), puis convertit les données
   reçues en objets Python utilisables par le programme.

3. **Dans `http://localhost:8000/v1/predict` :**
   - `localhost` désigne la machine locale ;
   - `8000` est le port d'écoute du serveur ;
   - `/v1/predict` est le chemin de la ressource de prédiction, version 1.

4. **Pourquoi `/v1` dans l'adresse ?**  
   Cela permet de versionner l'API. Une future version `/v2` pourra évoluer
   sans casser immédiatement les clients qui utilisent `/v1`.

5. **Dans `uvicorn maintai.api.main:app` :**  
   `maintai.api.main` désigne le module Python contenant l'API, et `app`
   désigne l'objet `FastAPI` que Uvicorn doit démarrer.




