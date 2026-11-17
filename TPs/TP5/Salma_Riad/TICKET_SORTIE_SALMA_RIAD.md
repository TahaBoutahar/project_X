# Ticket de sortie — Séance 7

**Nom : Salma Riad**  
**Groupe : à compléter**

**1. Qu'est-ce que le MLOps ajoute au DevOps ?**  
Le DevOps suit les changements du code et automatise son intégration et sa livraison. Le MLOps ajoute le suivi des versions des données, des modèles, des expériences et de leurs métriques, afin de gérer aussi la dérive des données et le réentraînement.

**2. Que versionnent Git, DVC et MLflow ?**  
Git versionne le code et les métadonnées DVC ; DVC versionne les jeux de données ; MLflow suit les entraînements (paramètres, métriques, modèles et dépendances).

**3. Pourquoi `data/sensors.csv` n'est-il pas dans Git ?**  
Pour éviter de conserver de gros fichiers et leurs versions dans le dépôt. DVC garde les données dans son cache et dans un stockage, et Git conserve le fichier léger `.dvc`.

**4. À partir d'un run MLflow, comment retrouver ses données ?**  
Lire le paramètre `data_md5` du run, identifier la version correspondante dans le fichier `data/sensors.csv.dvc` d'un commit Git, puis restaurer cette version avec `dvc checkout` ou `dvc pull`.

**5. Qu'est-ce qui reste flou pour vous ?**  
Point restant à pratiquer : la différence entre `dvc checkout` (restauration depuis le cache) et `dvc pull` (récupération depuis le stockage et restauration).
