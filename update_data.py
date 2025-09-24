import os
import pandas as pd
from edb_noumea.main import get_water_quality
from edb_noumea.details import get_detailed_results

def run_update():
    """
    Génère les dataframes et les sauvegarde en CSV.
    """
    print("Génération des dataframes...")

    # Assurez-vous que ces noms de fonction (get_resume, get_details)
    # correspondent bien à ceux de votre module.
    resume_df = get_water_quality()
    details_df = get_detailed_results()

    print("Dataframes générés avec succès.")

    # Créer le répertoire de sortie s'il n'existe pas
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)

    # Définir les chemins des fichiers de sortie
    resume_path = os.path.join(output_dir, 'resume.csv')
    details_path = os.path.join(output_dir, 'details.csv')

    # Sauvegarder en CSV
    resume_df.to_csv(resume_path, index=False)
    details_df.to_csv(details_path, index=False)

    print(f"Fichiers CSV sauvegardés dans '{output_dir}'.")

if __name__ == "__main__":
    run_update()
