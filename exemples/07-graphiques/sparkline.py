"""Mini-courbe en caractères (sparkline), sans librairie, lisible dans une notification.

    python exemples/07-graphiques/sparkline.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # pour importer exemples/slack.py
import slack

BARRES = "▁▂▃▄▅▆▇█"


def sparkline(valeurs):
    mini, maxi = min(valeurs), max(valeurs)
    ecart = (maxi - mini) or 1
    return "".join(BARRES[round((v - mini) / ecart * (len(BARRES) - 1))] for v in valeurs)


def variation(valeurs):
    if not valeurs[0]:
        return ""
    pct = (valeurs[-1] - valeurs[0]) / valeurs[0] * 100
    return f"{pct:+.1f} %".replace(".", ",")


if __name__ == "__main__":
    series = {
        "Visites": [1200, 1350, 1280, 1500, 1720, 1690, 1850],
        "Commandes": [85, 92, 88, 79, 70, 66, 61],
        "Temps de réponse (ms)": [210, 205, 220, 480, 900, 230, 215],
    }
    lignes = [f"`{sparkline(v)}`  *{nom}* : {v[-1]:,} ".replace(",", " ") + variation(v) for nom, v in series.items()]
    slack.envoyer("*Tendances sur 7 jours*\n" + "\n".join(lignes))
    print("\n".join(lignes))
