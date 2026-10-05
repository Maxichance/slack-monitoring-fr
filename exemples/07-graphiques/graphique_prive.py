"""Graphique privé : dessiné en local avec matplotlib puis envoyé comme fichier.

    pip install matplotlib
    python exemples/07-graphiques/graphique_prive.py

Les données ne quittent pas votre machine, à part vers Slack. C'est la méthode à utiliser
pour toute donnée interne ou sensible. Droit requis : files:write.
"""
import io
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # sans fenêtre, nécessaire sur un serveur ou dans une tâche planifiée
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # pour importer exemples/slack.py
import slack


def figure_en_png(fig):
    tampon = io.BytesIO()
    fig.savefig(tampon, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return tampon.getvalue()


if __name__ == "__main__":
    jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    cette_semaine = [1200, 1350, 1280, 1500, 1720, 1690, 1850]
    semaine_derniere = [1100, 1180, 1250, 1300, 1400, 1520, 1480]

    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.plot(jours, cette_semaine, color="#2EB67D", linewidth=2.5, marker="o", label="Cette semaine")
    ax.plot(jours, semaine_derniere, color="#9AA0A6", linewidth=1.5, linestyle="--", label="Semaine dernière")
    ax.set_title("Visites par jour", loc="left", fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(frameon=False)
    png = figure_en_png(fig)

    # 1. Comme fichier (avec un commentaire) : la façon la plus simple.
    id_fichier = slack.joindre_fichier(png, "visites.png", "Visites par jour",
                                       commentaire="*Visites par jour* (graphique généré avec matplotlib)")

    # 2. Réutiliser le fichier dans un message Block Kit (attendre que Slack l'ait traité).
    if id_fichier:
        time.sleep(4)
        slack.envoyer("Graphique dans un message", blocks=[
            {"type": "section", "text": {"type": "mrkdwn", "text": "*Le même graphique, intégré dans un message Block Kit*"}},
            {"type": "image", "slack_file": {"id": id_fichier}, "alt_text": "Visites par jour"},
        ])
    print("Graphique envoyé" if id_fichier else "Échec de l'envoi")
