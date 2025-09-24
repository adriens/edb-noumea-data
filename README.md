# Données sur la Qualité des Eaux de Baignade à Nouméa

Ce dépôt contient les données sur la qualité des eaux de baignade pour les plages de Nouméa. Les données sont collectées et mises à jour automatiquement.

## Fichiers de Données

Les données sont stockées dans le dossier `data/` et se composent de deux fichiers :

- `data/resume.csv`: Un fichier résumé de l'état de la baignade pour différentes plages.
- `data/details.csv`: Un fichier détaillé avec plus d'informations pour chaque relevé.

## Mise à Jour Automatique

Un workflow GitHub Actions s'exécute **tous les jours à 5h00 UTC** pour mettre à jour les fichiers CSV. 

Le processus est le suivant :
1.  Le script `update_data.py` est lancé.
2.  Il utilise la bibliothèque [edb-noumea](https://github.com/adriens/edb-noumea) pour récupérer les dernières données.
3.  Les nouveaux fichiers `resume.csv` et `details.csv` sont générés.
4.  Les fichiers mis à jour sont automatiquement commités sur ce dépôt.

## Utilisation Locale

Pour exécuter le script de mise à jour manuellement :

1.  **Clonez le dépôt :**
    ```bash
    git clone https://github.com/adriens/edb-noumea-data.git
    cd edb-noumea-data
    ```

2.  **Installez les dépendances :**
    ```bash
    uv pip install -r requirements.txt
    ```

3.  **Exécutez le script :**
    ```bash
    python update_data.py
    ```

4.  Les fichiers CSV seront générés ou mis à jour dans le dossier `data/`.
