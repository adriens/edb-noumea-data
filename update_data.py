import os
import pandas as pd
from edb_noumea.main import get_water_quality
from edb_noumea.details import get_detailed_results

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

    # Récupérer les détails (avec gestion d'erreur si PDF indisponible)
    try:
        details_df = get_detailed_results()
        if details_df is not None:
            # Nettoyage : supprimer les lignes où le site est manquant (évite la ligne vide après l'entête)
            details_df = details_df.dropna(subset=['site'])
            
            details_path = os.path.join(output_dir, 'details.csv')
            details_df.to_csv(details_path, index=False)
            print(f"Détails sauvegardés dans '{details_path}'.")
        else:
            print("⚠️  PDF indisponible : impossible de récupérer les détails.")
            print("Le fichier resume.csv a été généré avec succès.")
    except Exception as e:
        print(f"Erreur lors de la récupération des détails (PDF peut-être indisponible): {e}")
        print("Le fichier resume.csv a été généré avec succès.")

    print(f"Mise à jour terminée.")

if __name__ == "__main__":
    run_update()
