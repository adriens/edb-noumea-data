"""
Reconstruit l'historique complet des données de baignade à partir de l'historique git.

Les fichiers data/resume.csv et data/details.csv sont écrasés à chaque mise à jour
automatique : seul l'état courant y est visible. L'historique complet existe malgré
tout, dispersé dans les commits git. Ce script parcourt tous les commits du dépôt et
reconstruit :
  - data/details_history.csv : toutes les mesures (E. coli / entérocoques) jamais
    publiées, dédupliquées par point de prélèvement + date + heure.
  - data/resume_history.csv : l'état sanitaire de chaque plage à la date de chaque
    commit qui a modifié resume.csv (une ligne par plage et par changement d'état).

Peut être relancé à tout moment : il repart de zéro à partir de git et écrase les
deux fichiers de sortie.
"""
import subprocess
import pandas as pd
from io import StringIO

REPO_DETAILS = "data/details.csv"
REPO_RESUME = "data/resume.csv"


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def commits_touching(path):
    """Retourne (sha, date_iso) pour chaque commit touchant `path`, du plus ancien au plus récent."""
    out = git("log", "--format=%H|%aI", "--reverse", "--", path)
    commits = []
    for line in out.strip().splitlines():
        sha, date = line.split("|", 1)
        commits.append((sha, date[:10]))
    return commits


def show_file(sha, path):
    try:
        return git("show", f"{sha}:{path}")
    except subprocess.CalledProcessError:
        return None


def rebuild_details():
    frames = []
    for sha, _ in commits_touching(REPO_DETAILS):
        content = show_file(sha, REPO_DETAILS)
        if not content:
            continue
        df = pd.read_csv(StringIO(content))
        df = df.dropna(subset=["site"])
        frames.append(df)

    all_rows = pd.concat(frames, ignore_index=True)
    key = ["id_point_prelevement", "date", "heure"]
    all_rows = all_rows.drop_duplicates(subset=key, keep="last")
    all_rows = all_rows.sort_values(["date", "heure", "site"]).reset_index(drop=True)
    all_rows.to_csv("data/details_history.csv", index=False)
    print(f"data/details_history.csv : {len(all_rows)} relevés ({all_rows['date'].nunique()} dates distinctes).")


def rebuild_resume():
    frames = []
    for sha, date in commits_touching(REPO_RESUME):
        content = show_file(sha, REPO_RESUME)
        if not content:
            continue
        df = pd.read_csv(StringIO(content))
        df.insert(0, "date_changement", date)
        frames.append(df)

    all_rows = pd.concat(frames, ignore_index=True)
    # Une même mise à jour peut ne rien changer pour une plage donnée : on ne garde
    # que les lignes où l'état sanitaire diffère du relevé précédent pour cette plage.
    all_rows = all_rows.sort_values(["plage", "date_changement"])
    previous_state = all_rows.groupby("plage")["etat_sanitaire"].shift()
    changed = all_rows[all_rows["etat_sanitaire"].ne(previous_state)]
    changed = changed.sort_values(["date_changement", "plage"]).reset_index(drop=True)
    changed.to_csv("data/resume_history.csv", index=False)
    print(f"data/resume_history.csv : {len(changed)} changements d'état enregistrés.")


if __name__ == "__main__":
    rebuild_details()
    rebuild_resume()
