"""Rapport quotidien complet : tout assemblé en un seul message (titre, chiffres clés,
tendances, tableau, bouton), avec le détail en CSV dans le fil.

    python exemples/09-rapport-quotidien/rapport_quotidien.py

À planifier chaque matin (voir exemples/04-vigie/README.md). Envoyé même quand tout va bien,
il confirme aussi que la surveillance elle-même fonctionne.
"""
import sys
import time
from pathlib import Path

DOSSIER_EXEMPLES = Path(__file__).resolve().parent.parent
for sous_dossier in ("", "06-tableaux", "07-graphiques"):
    sys.path.insert(0, str(DOSSIER_EXEMPLES / sous_dossier))
import slack  # noqa: E402
from sparkline import sparkline, variation  # noqa: E402
from tableaux import bloc_tableau  # noqa: E402

# Données de démonstration : remplacez-les par vos vraies mesures.
INDICATEURS = {
    "Visites": [1200, 1350, 1280, 1500, 1720, 1690, 1850],
    "Commandes": [85, 92, 88, 79, 70, 66, 61],
    "Taux d'erreur (%)": [0.4, 0.3, 0.5, 0.4, 0.6, 0.5, 0.4],
}
SOURCES = [["Source A", "12 400", "✅"], ["Source B", "8 210", "✅"], ["Source C", "0", "❌"]]
LIEN_TABLEAU_DE_BORD = "https://example.com/dashboard"


def nombre(v):
    return f"{v:,}".replace(",", " ") if isinstance(v, int) else f"{v:g}".replace(".", ",")


if __name__ == "__main__":
    maintenant = int(time.time())
    problemes = sum(ligne[-1] == "❌" for ligne in SOURCES)
    statut = "✅ Tout est normal" if not problemes else f"⚠️ {problemes} point(s) d'attention"

    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": "Rapport du jour"}},
        {"type": "context", "elements": [{"type": "mrkdwn",
            "text": f"<!date^{maintenant}^{{date_long_pretty}} à {{time}}|aujourd'hui> · {statut}"}]},
        {"type": "section", "fields": [
            {"type": "mrkdwn", "text": f"*{nom}*\n{nombre(v[-1])}  {variation(v)}\n`{sparkline(v)}`"}
            for nom, v in INDICATEURS.items()]},
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*État des sources*"}},
        bloc_tableau(["Source", "Lignes", "Statut"], SOURCES),
        {"type": "actions", "elements": [{"type": "button", "style": "primary",
            "text": {"type": "plain_text", "text": "Ouvrir le tableau de bord"}, "url": LIEN_TABLEAU_DE_BORD}]},
    ]
    ts = slack.envoyer(f"Rapport du jour · {statut}", blocks=blocks)

    csv = "source;lignes;statut\n" + "\n".join(";".join(l).replace("✅", "OK").replace("❌", "ECHEC") for l in SOURCES)
    slack.joindre_fichier(csv.encode("utf-8-sig"), "rapport_du_jour.csv", "Détail du rapport", fil=ts)
    print("Rapport envoyé" if ts else "Échec de l'envoi")
