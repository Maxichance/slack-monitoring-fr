"""Joindre des fichiers : log, CSV, Excel. Droit requis : files:write.

    python exemples/08-fichiers/fichiers.py
    (pip install openpyxl pour l'exemple Excel, facultatif)
"""
import csv
import io
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # pour importer exemples/slack.py
import slack

DONNEES = [
    {"source": "Source A", "lignes": 12400, "statut": "OK"},
    {"source": "Source B", "lignes": 8210, "statut": "OK"},
    {"source": "Source C", "lignes": 0, "statut": "ECHEC"},
]

if __name__ == "__main__":
    ts = slack.envoyer("*Exemples de fichiers joints* (voir le fil)")

    # 1. Un log : le plus utile en cas d'échec (texte brut, aucune librairie)
    log = "\n".join(f"[{datetime.now():%H:%M:%S}] {d['source']} : {d['lignes']} lignes ({d['statut']})" for d in DONNEES)
    slack.joindre_fichier(log, "execution.log", "Log de l'exécution", fil=ts)

    # 2. Un CSV : s'ouvre dans Excel. Le BOM (utf-8-sig) et le « ; » évitent les problèmes d'accents et de colonnes.
    tampon = io.StringIO()
    ecrivain = csv.DictWriter(tampon, fieldnames=DONNEES[0].keys(), delimiter=";")
    ecrivain.writeheader()
    ecrivain.writerows(DONNEES)
    slack.joindre_fichier(tampon.getvalue().encode("utf-8-sig"), "sources.csv", "Export des sources",
                          commentaire="Export CSV", fil=ts)

    # 3. Un vrai fichier Excel (si openpyxl est installé)
    try:
        from openpyxl import Workbook
        classeur = Workbook()
        feuille = classeur.active
        feuille.append(list(DONNEES[0].keys()))
        for d in DONNEES:
            feuille.append(list(d.values()))
        tampon_xlsx = io.BytesIO()
        classeur.save(tampon_xlsx)
        slack.joindre_fichier(tampon_xlsx.getvalue(), "sources.xlsx", "Export Excel", fil=ts)
    except ImportError:
        print("openpyxl non installé : exemple Excel ignoré")

    print("Fichiers envoyés dans le fil")
