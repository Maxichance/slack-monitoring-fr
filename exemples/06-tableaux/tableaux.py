"""Trois façons d'afficher un tableau dans Slack.

    python exemples/06-tableaux/tableaux.py

1. Bloc « table » : un vrai tableau, le plus lisible (un seul par message).
2. Colonnes      : chiffres clés sur deux colonnes (10 cases au maximum), adapté à un résumé.
3. Bloc de code  : texte aligné, lisible partout, y compris dans les notifications.
Pour un tableau volumineux, joignez plutôt un CSV (voir 08-fichiers).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # pour importer exemples/slack.py
import slack

ENTETES = ["Source", "Lignes", "Variation", "Statut"]
LIGNES = [
    ["Source A", "12 400", "+4,2 %", "✅"],
    ["Source B", "8 210", "-1,3 %", "✅"],
    ["Source C", "0", "-100 %", "❌"],
]


def bloc_tableau(entetes, lignes):
    """Bloc Block Kit « table » (cellules texte)."""
    def cellule(texte):
        return {"type": "raw_text", "text": str(texte)}
    return {"type": "table",
            "column_settings": [{"is_wrapped": True}] + [{"align": "right"}] * (len(entetes) - 1),
            "rows": [[cellule(c) for c in entetes]] + [[cellule(c) for c in ligne] for ligne in lignes]}


def bloc_colonnes(chiffres):
    """Section à 2 colonnes : {"Libellé": "valeur", …} (10 cases maximum)."""
    return {"type": "section", "fields": [{"type": "mrkdwn", "text": f"*{k}*\n{v}"} for k, v in chiffres.items()]}


def tableau_texte(entetes, lignes):
    """Tableau aligné en texte, à placer dans un bloc de code."""
    largeurs = [max(len(str(x)) for x in colonne) for colonne in zip(entetes, *lignes)]
    def formater(ligne):
        return "  ".join(str(c).ljust(l) if i == 0 else str(c).rjust(l) for i, (c, l) in enumerate(zip(ligne, largeurs)))
    return "\n".join([formater(entetes), "  ".join("-" * l for l in largeurs)] + [formater(l) for l in lignes])


if __name__ == "__main__":
    slack.envoyer("Tableau : bloc table", blocks=[
        {"type": "section", "text": {"type": "mrkdwn", "text": "*1. Bloc « table »*"}},
        bloc_tableau(ENTETES, LIGNES),
    ])
    slack.envoyer("Tableau : colonnes", blocks=[
        {"type": "section", "text": {"type": "mrkdwn", "text": "*2. Chiffres clés en colonnes*"}},
        bloc_colonnes({"Lignes traitées": "20 610", "Sources OK": "2 / 3", "Durée": "00:03:41", "Statut": "⚠️ partiel"}),
    ])
    # Les emojis n'ont pas tous la même largeur : dans un bloc de code, préférez des mots (OK / ECHEC).
    lignes_texte = [[c.replace("✅", "OK").replace("❌", "ECHEC") for c in l] for l in LIGNES]
    slack.envoyer("*3. Bloc de code aligné*\n```" + tableau_texte(ENTETES, lignes_texte) + "```")
    print("3 tableaux envoyés")
