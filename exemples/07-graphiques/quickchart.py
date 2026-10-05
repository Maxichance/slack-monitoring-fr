"""Graphique sans installation avec QuickChart.io (configuration Chart.js → URL d'image).

    python exemples/07-graphiques/quickchart.py

Attention : les données sont envoyées à un service externe et l'image obtenue est PUBLIQUE
(toute personne qui a l'URL peut la voir). Réservé aux données non sensibles :
sinon, utilisez graphique_prive.py.
Documentation des graphiques : https://quickchart.io/documentation/ et https://www.chartjs.org/
"""
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # pour importer exemples/slack.py
import slack


def url_graphique(config, largeur=600, hauteur=300):
    """Renvoie l'URL courte d'une image (les URL longues dépassent la limite de 3 000 caractères de Slack)."""
    try:
        r = requests.post("https://quickchart.io/chart/create",
                          json={"chart": config, "width": largeur, "height": hauteur,
                                "backgroundColor": "white", "version": "4"}, timeout=15)
        return r.json().get("url") if r.ok else None
    except requests.RequestException:
        return None


def image_disponible(url):
    """Évite l'erreur invalid_blocks si le service ne renvoie pas d'image."""
    try:
        r = requests.get(url, timeout=10, stream=True)
        return r.ok and r.headers.get("Content-Type", "").startswith("image/")
    except requests.RequestException:
        return False


if __name__ == "__main__":
    jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    config = {
        "type": "line",
        "data": {"labels": jours, "datasets": [
            {"label": "Cette semaine", "data": [1200, 1350, 1280, 1500, 1720, 1690, 1850],
             "borderColor": "#2EB67D", "tension": 0.3},
            {"label": "Semaine dernière", "data": [1100, 1180, 1250, 1300, 1400, 1520, 1480],
             "borderColor": "#9AA0A6", "borderDash": [6, 4], "tension": 0.3},
        ]},
        "options": {"plugins": {"title": {"display": True, "text": "Visites par jour"}}},
    }
    url = url_graphique(config)
    if url and image_disponible(url):
        slack.envoyer("Visites par jour", blocks=[
            {"type": "section", "text": {"type": "mrkdwn", "text": "*Visites par jour* (QuickChart)"}},
            {"type": "image", "image_url": url, "alt_text": "Visites par jour"},
        ])
        print("Graphique envoyé :", url)
    else:
        slack.envoyer("Visites par jour : graphique indisponible (service QuickChart injoignable)")
        print("QuickChart indisponible : message envoyé sans image")
