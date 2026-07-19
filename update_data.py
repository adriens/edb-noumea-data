import os
from datetime import timezone, datetime

import pandas as pd
from edb_noumea.main import get_water_quality
from edb_noumea.details import get_detailed_results


def append_details_history(details_df, output_dir):
    """Ajoute les nouveaux relevés à l'historique complet, sans doublons."""
    history_path = os.path.join(output_dir, 'details_history.csv')
    key = ['id_point_prelevement', 'date', 'heure']

    details_df = details_df.copy()
    # Normalise la date en chaîne 'YYYY-MM-DD' : get_detailed_results() la renvoie
    # parfois en datetime64, ce qui casse la clé de déduplication (mélange de types
    # 'objet' où les Timestamp s'affichent avec " 00:00:00" au moment du to_csv).
    details_df['date'] = pd.to_datetime(details_df['date']).dt.strftime('%Y-%m-%d')

    if os.path.exists(history_path):
        history_df = pd.read_csv(history_path)
        combined = pd.concat([history_df, details_df], ignore_index=True)
    else:
        combined = details_df.copy()

    combined = combined.drop_duplicates(subset=key, keep='last')
    combined = combined.sort_values(['date', 'heure', 'site']).reset_index(drop=True)
    combined.to_csv(history_path, index=False)
    print(f"Historique des détails mis à jour dans '{history_path}' ({len(combined)} relevés).")


def append_resume_history(resume_df, output_dir):
    """Ajoute une ligne d'historique pour chaque plage dont l'état sanitaire a changé."""
    history_path = os.path.join(output_dir, 'resume_history.csv')
    today = datetime.now(timezone.utc).date().isoformat()

    snapshot = resume_df.copy()
    snapshot.insert(0, 'date_changement', today)

    if os.path.exists(history_path):
        history_df = pd.read_csv(history_path)
        last_state = (
            history_df.sort_values('date_changement')
            .groupby('plage')['etat_sanitaire']
            .last()
        )
        is_new = snapshot.apply(
            lambda row: last_state.get(row['plage']) != row['etat_sanitaire'], axis=1
        )
        new_rows = snapshot[is_new]
        combined = pd.concat([history_df, new_rows], ignore_index=True)
    else:
        combined = snapshot

    combined = combined.sort_values(['date_changement', 'plage']).reset_index(drop=True)
    combined.to_csv(history_path, index=False)
    print(f"Historique du résumé mis à jour dans '{history_path}' ({len(combined)} changements d'état).")


def run_update():
    """
    Génère les dataframes et les sauvegarde en CSV.
    """
    print("Génération des dataframes...")

    # Créer le répertoire de sortie s'il n'existe pas
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)

    # Récupérer le résumé
    resume_df = get_water_quality()
    resume_path = os.path.join(output_dir, 'resume.csv')
    resume_df.to_csv(resume_path, index=False)
    print(f"Résumé sauvegardé dans '{resume_path}'.")
    append_resume_history(resume_df, output_dir)

    # Récupérer les détails (avec gestion d'erreur si PDF indisponible)
    try:
        details_df = get_detailed_results()
        if details_df is not None:
            # Nettoyage : supprimer les lignes où le site est manquant (évite la ligne vide après l'entête)
            details_df = details_df.dropna(subset=['site'])
            # L'extraction PDF (Camelot) laisse parfois passer une ligne d'en-tête
            # dupliquée ou une ligne quasi vide ; on ne garde que les relevés dont
            # l'identifiant de point de prélèvement a la forme attendue "P" + chiffres.
            details_df = details_df[details_df['id_point_prelevement'].astype(str).str.match(r'^P\d+$')]

            details_path = os.path.join(output_dir, 'details.csv')
            details_df.to_csv(details_path, index=False)
            print(f"Détails sauvegardés dans '{details_path}'.")
            append_details_history(details_df, output_dir)
        else:
            print("⚠️  PDF indisponible : impossible de récupérer les détails.")
            print("Le fichier resume.csv a été généré avec succès.")
    except Exception as e:
        print(f"Erreur lors de la récupération des détails (PDF peut-être indisponible): {e}")
        print("Le fichier resume.csv a été généré avec succès.")

    print(f"Mise à jour terminée.")

if __name__ == "__main__":
    run_update()
