"""Vérifie que des données sont bien mises à jour (un export, une sauvegarde, la sortie d'un job…).

    python exemples/04-vigie/surveiller_fraicheur.py --demo

Un job planifié qui ne se lance plus n'envoie aucune erreur : seule une vérification
extérieure remarque que les fichiers ne sont plus mis à jour.

Usage réel :
    verifier_fraicheur("Export quotidien", "D:/exports/*.csv", max_heures=26)
"""
import glob
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

from vigie import duree_lisible, signaler


def verifier_fraicheur(nom, motif, max_heures):
    """Alerte si le fichier le plus récent correspondant au motif a plus de `max_heures`."""
    fichiers = glob.glob(motif)
    if not fichiers:
        return signaler(f"fraicheur:{motif}", "erreur", nom, "Aucun fichier trouvé",
                        {"Emplacement": motif}, source="vigie · fraîcheur")
    plus_recent = max(fichiers, key=os.path.getmtime)
    age = time.time() - os.path.getmtime(plus_recent)
    champs = {"Dernier fichier": Path(plus_recent).name,
              "Mis à jour le": datetime.fromtimestamp(os.path.getmtime(plus_recent)).strftime("%d/%m/%Y %H:%M"),
              "Âge": duree_lisible(age), "Maximum toléré": f"{max_heures} h"}
    statut = "erreur" if age > max_heures * 3600 else "ok"
    return signaler(f"fraicheur:{motif}", statut, nom, "Les données ne sont plus mises à jour",
                    champs, source="vigie · fraîcheur")


if __name__ == "__main__":
    if "--demo" not in sys.argv:
        print("Lancez avec --demo, ou importez verifier_fraicheur dans votre script.")
        sys.exit(0)
    dossier = Path(tempfile.gettempdir()) / "demo_vigie_fraicheur"
    dossier.mkdir(exist_ok=True)
    fichier = dossier / "export_du_jour.csv"
    fichier.write_text("id;valeur\n1;42\n", encoding="utf-8")
    il_y_a_30h = time.time() - 30 * 3600
    os.utime(fichier, (il_y_a_30h, il_y_a_30h))       # simule un export vieux de 30 h
    print("Export vieux de 30 h →", verifier_fraicheur("Export quotidien (démo)", str(dossier / "*.csv"), 26))
    time.sleep(1.5)
    fichier.touch()                                     # l'export repart
    print("Export rafraîchi    →", verifier_fraicheur("Export quotidien (démo)", str(dossier / "*.csv"), 26))
