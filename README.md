[![PyPI version](https://img.shields.io/pypi/v/edb-noumea.svg?label=edb-noumea&logo=pypi)](https://pypi.org/project/edb-noumea/)
[![Go BubbleTea TUI](https://img.shields.io/badge/Go-BubbleTea%20TUI-00ADD8?logo=go)](https://github.com/adriens/edb-noumea-tui)


# Données sur la Qualité des Eaux de Baignade à Nouméa

Ce dépôt contient les données sur la qualité des eaux de baignade pour les plages de Nouméa. Les données sont collectées et mises à jour automatiquement.

## Fichiers de Données

Les données sont stockées dans le dossier `data/` et se composent de quatre fichiers :

- `data/resume.csv`: L'état sanitaire courant de chaque plage (snapshot, écrasé à chaque mise à jour).
- `data/details.csv`: Le dernier relevé détaillé (E. coli / entérocoques) par point de prélèvement (snapshot, écrasé à chaque mise à jour).
- `data/resume_history.csv`: L'historique des changements d'état sanitaire par plage (une ligne à chaque fois que l'état d'une plage change).
- `data/details_history.csv`: L'historique complet de tous les relevés détaillés jamais publiés, dédupliqués par point de prélèvement + date + heure.

## Mise à Jour Automatique

Un workflow GitHub Actions s'exécute **tous les jours à 5h00 UTC** pour mettre à jour les fichiers CSV. 

Le processus est le suivant :
1.  Le script `update_data.py` est lancé.
2.  Il utilise la bibliothèque [edb-noumea](https://github.com/adriens/edb-noumea) pour récupérer les dernières données.
3.  Les nouveaux fichiers `resume.csv` et `details.csv` sont générés (snapshot courant).
4.  Les fichiers d'historique `resume_history.csv` et `details_history.csv` sont mis à jour de façon incrémentale (ajout des nouveautés, sans doublons).
5.  Les fichiers mis à jour sont automatiquement commités sur ce dépôt.

### Reconstruire l'historique depuis git

Avant la mise en place de l'historique incrémental, les seules traces des relevés passés étaient dans les commits git (les CSV étant écrasés à chaque run). Le script `scripts/rebuild_history.py` reconstruit `data/details_history.csv` et `data/resume_history.csv` en parcourant tout l'historique git :

```bash
python scripts/rebuild_history.py
```

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
