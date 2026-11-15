# Étude de conception — Prévision de la consommation électrique d’un bâtiment (EnergyForecast)

## 1. Contexte et utilisateurs

- **Organisation ou situation :** gestionnaire d'un bâtiment tertiaire (bureaux ou établissement d'enseignement) souhaitant anticiper sa consommation électrique pour mieux organiser les usages et identifier les périodes de forte demande.
- **Utilisateur principal :** responsable technique ou gestionnaire énergétique du bâtiment.
- **Objectif :** fournir une estimation de la consommation électrique future (en kWh) à partir de l'historique et de variables disponibles au moment de la prévision.

## 2. Problème et décision

- **Décision prise avec le système :** anticiper les pics de consommation, planifier des actions d'économie d'énergie et comparer les prévisions aux mesures réelles.
- **Fréquence :** prévision horaire, mise à jour lorsque de nouvelles mesures sont disponibles.
- **Conséquence d'une erreur :** une sous-estimation peut empêcher d'anticiper un pic ; une surestimation peut conduire à des mesures d'économie inutiles. Les prédictions restent une aide à la décision, sans commande automatique d'équipements.

## 3. Approche par sous-problème

| Sous-problème | Approche retenue | Pourquoi cette approche ? |
|---|---|---|
| 1. Préparer les données | Nettoyage, gestion des valeurs manquantes, création de variables calendaires et de retards (*lags*) | Les relevés temporels peuvent être incomplets et la consommation dépend des heures et des jours. |
| 2. Prévoir la consommation | Régression ML : `RandomForestRegressor` ou `HistGradientBoostingRegressor` | Modèles adaptés aux données tabulaires et aux relations non linéaires. |
| 3. Comparer et expliquer | Baseline « même heure la veille », MAE/RMSE et importance des variables | Vérifier que le ML apporte un gain réel et rendre les résultats compréhensibles. |
| 4. Restituer la prévision | Interface Streamlit et API FastAPI | Permettre la saisie, l'affichage d'une estimation et des graphiques. |

> **Périmètre :** le projet utilise du Machine Learning supervisé. Aucun assistant RAG n'est nécessaire : il est optionnel dans les consignes du cours.

## 4. Données

| Jeu de données envisagé | Source et licence | Contenu utile | Données personnelles ? |
|---|---|---|---|
| **Individual Household Electric Power Consumption** | UCI Machine Learning Repository — vérifier les conditions de réutilisation sur la fiche officielle avant diffusion | Mesures électriques horodatées d'un foyer, agrégées à l'heure si nécessaire | Pas d'identifiants directs dans les variables décrites ; vérifier le contenu et les conditions de diffusion |

**Lien de référence :** https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption

**Point de vigilance :** ce dataset concerne **un foyer**, pas un bâtiment tertiaire. Pour conserver strictement le sujet « bâtiment », il faudra soit trouver un dataset de bâtiment (bureaux, école, etc.), soit présenter le foyer comme un bâtiment résidentiel et adapter explicitement le périmètre. La variable cible et les unités seront définies après inspection du dataset choisi. Les variables de température, d'humidité et d'occupation ne devront pas être affichées comme entrées si elles ne figurent pas dans les données ou ne sont pas obtenues d'une source fiable.

**Préparation envisagée :** analyse des dates, doublons, trous de mesure, valeurs aberrantes ; agrégation horaire ; création de variables `heure`, `jour_semaine`, `mois`, et consommation passée. Les variables historiques doivent être calculées sans utiliser d'informations futures.

## 5. Métriques, baseline et critères d'acceptation

- **Baseline :** prévoir la consommation d'une heure à partir de la consommation observée à la même heure la veille (lorsqu'elle est disponible).
- **Métrique principale :** MAE (erreur absolue moyenne, en kWh) : elle exprime directement l'écart moyen entre prévision et réalité.
- **Métriques complémentaires :** RMSE (pénalise les grosses erreurs) et éventuellement WAPE si le dénominateur est pertinent.
- **Validation :** découpage chronologique entraînement / validation / test, sans mélange aléatoire ; le test représente la période la plus récente.
- **Critères d'acceptation :** (1) API `/predict` fonctionnelle et documentée ; (2) le modèle obtient une MAE sur test inférieure à celle de la baseline ; (3) tests automatisés des entrées et de l'API ; (4) démarrage reproductible avec Docker ; (5) résultats consignés dans MLflow et données/pipeline suivis avec DVC si requis par le professeur.

Les seuils numériques de performance seront fixés après une première exploration : aucun score n'est inventé à ce stade.

## 6. Architecture prévue

```text
Dataset (CSV / mesures horodatées)
              |
              v
Nettoyage + agrégation + variables temporelles
              |
              v
Entraînement et évaluation (scikit-learn)
              |              \
              v               v
Modèle sauvegardé       Suivi MLflow / DVC
              |
              v
API FastAPI (/predict, /health, /docs)
              |
              v
Interface Streamlit (saisie, résultats, graphiques)
              |
              v
Conteneurisation Docker + tests
```

**Parcours utilisateur :** choisir une date/heure de prévision, renseigner uniquement les paramètres effectivement disponibles, cliquer sur **Prédire**, consulter la consommation estimée et les graphiques historiques. Si des données historiques sont indispensables au modèle, elles seront chargées automatiquement depuis le jeu de données ou une source de mesures, et non inventées par l'utilisateur.

**API :**
- `GET /health` : état du service.
- `POST /predict` : validation des données entrantes et renvoi de la consommation estimée avec son unité et l'horizon de prévision.
- `GET /docs` : documentation OpenAPI générée par FastAPI.

**Sécurité :** validation Pydantic, clé API configurable par variable d'environnement pour l'accès à `/predict`, absence de secrets dans GitHub, journalisation sans données sensibles.

## 7. Choix technologiques

| Brique fonctionnelle | Technologie retenue | Justification |
|---|---|---|
| Langage | Python 3.11+ | Écosystème ML et API accessible. |
| Traitement | pandas, NumPy | Manipulation des séries temporelles. |
| Machine Learning | scikit-learn | Modèles de régression, pipelines et métriques. |
| Backend API | FastAPI, Pydantic, Uvicorn | Validation des entrées, service REST et documentation. |
| Interface | Streamlit | Tableau de bord rapide à développer. |
| Tests | pytest | Tests unitaires et d'intégration. |
| Suivi d'expériences | MLflow | Comparaison des entraînements et des métriques. |
| Versionnement des données | DVC | Reproductibilité des jeux de données et pipelines. |
| Déploiement | Docker | Environnement reproductible. |
| Versionnement du code | Git / GitHub | Historique et collaboration. |

## 8. Risques, éthique et confidentialité : huit questions

1. **Les données contiennent-elles des données personnelles ?** Les relevés énergétiques peuvent révéler des habitudes de présence ; les jeux de données doivent être vérifiés avant publication.
2. **Peut-on s'en passer ou les anonymiser ?** Oui : privilégier des mesures agrégées et exclure adresses, noms et identifiants d'occupants.
3. **Qui peut être lésé par une erreur ?** Le gestionnaire et les occupants, si une décision de réduction de consommation est mal planifiée.
4. **Les données couvrent-elles tous les cas d'usage ?** Pas nécessairement : saisons, jours fériés et types de bâtiments peuvent être sous-représentés.
5. **Quelle erreur coûte le plus ?** Une sous-estimation des pics peut être plus problématique pour la planification ; ce choix dépend du contexte réel.
6. **Qui valide les décisions et peut corriger ?** Le gestionnaire humain ; l'interface doit signaler que la prévision est indicative.
7. **Les données sortent-elles de l'organisation ?** Déploiement local privilégié ; aucun envoi externe requis pour l'inférence.
8. **Comment détourner le système et être détecté ?** Des valeurs d'entrée falsifiées peuvent produire de mauvaises estimations ; appliquer validation, contrôles de plage et logs techniques.

## 9. Limites et hors périmètre

**Hors périmètre :**
- Pilotage automatique des appareils électriques ou des compteurs.
- Tarification et facturation officielles.
- Prévision fiable pour n'importe quel bâtiment sans réentraînement.
- Assistant documentaire RAG (optionnel, non retenu dans la version initiale).

**Limites :**
- La qualité des résultats dépend de la couverture temporelle et de la qualité des relevés.
- Un modèle entraîné sur un foyer résidentiel ne représente pas automatiquement un immeuble de bureaux.
- Les événements inhabituels (pannes, changements d'occupation, météo extrême) peuvent réduire la précision.
- La prévision d'une heure future nécessite une définition précise des variables connues au moment de la prédiction.

---

*Document de conception initial — les choix de données, variables et performances seront confirmés après exploration et validation du sujet avec le professeur.*
