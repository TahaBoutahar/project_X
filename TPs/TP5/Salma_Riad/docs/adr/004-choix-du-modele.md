# ADR 004 — Choix du modèle MaintAI

**Auteure : Salma Riad**  
**Statut : proposition, à confirmer par les runs MLflow**  
**Date : 17 novembre 2026**

## Contexte

MaintAI prédit des pannes de machines. Une panne non détectée est considérée comme plus coûteuse qu'une fausse alerte. La mesure prioritaire est donc le **rappel** (`recall`), sans ignorer la précision.

## Décision proposée

Sur la v1 synthétique et les résultats scikit-learn calculés localement, le meilleur rappel parmi les cinq réglages testés est obtenu avec **logreg seuil 0.2** (recall = **0.838**, précision = **0.543**). Nous proposons ce réglage, sous réserve de confirmer les mesures dans MLflow et d'évaluer le coût des fausses alertes.

## Compromis

Prioriser le rappel peut provoquer davantage de fausses alertes. Comparer avec le modèle forêt aléatoire et surveiller la précision.

## Traçabilité

- Jeu de données : v1, **5000 observations**.
- `data_md5` : `b7fec4274774842dc1f48202c6013490`.
- ID du run MLflow sélectionné : **À compléter après exécution** (ne pas inventer cet identifiant).
- Version de scikit-learn demandée par le starter : `1.8.0` ; à contrôler dans l'artefact du run.

## Conséquences

Le déploiement doit utiliser le modèle et le seuil correspondant au run retenu, tout en conservant l'empreinte exacte des données et les dépendances associées. Comparer sur des données de test communes avant de conclure à une amélioration définitive.
