# ADR 005 : modèle et données montés en volumes Docker

Date : 24/11/2026 · Auteurs : Salma Riad et BOUTAHAR MOHAMED TAHA

## Contexte
MaintAI doit pouvoir être exécuté sur un poste ou un serveur sans installer manuellement Python et ses bibliothèques. Le modèle entraîné, les données et la clé API évoluent indépendamment du code et ne doivent pas être intégrés à une image partageable.

## Options étudiées
1. **Inclure le modèle et les données dans l’image** : le déploiement est autonome, mais chaque changement du modèle ou des données impose de reconstruire et redistribuer l’image ; l’image devient plus lourde.
2. **Monter le modèle et les données par des volumes au lancement** : l’image reste légère et réutilisable, et les fichiers peuvent être mis à jour sans rebuild ; le déploiement doit fournir les dossiers attendus sur l’hôte.

## Décision
Le code et les dépendances sont intégrés à l’image `maintai:0.4.0`. Le modèle est monté en lecture seule depuis `./models` vers `/app/models` pour le service API, et les données depuis `./data` vers `/app/data` pour l’interface. La clé API est fournie au lancement par `env_file: .env` et n’est jamais copiée dans l’image.

## Conséquences
L’image peut être reconstruite et partagée sans embarquer les artefacts propres à une machine. Le modèle et les données doivent être présents dans les dossiers locaux avant le démarrage ; le fichier `.env` doit être créé à partir de `.env.example` et ne doit jamais être commité. Les volumes sont montés en lecture seule pour éviter leur modification par les conteneurs.
