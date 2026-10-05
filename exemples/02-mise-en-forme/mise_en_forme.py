"""Mises en forme de texte disponibles dans Slack, sans librairie.

    python exemples/02-mise-en-forme/mise_en_forme.py

Pour mentionner quelqu'un, renseignez SLACK_MENTION_ID dans le .env
(profil Slack → ⋮ → « Copier l'ID du membre », commence par U).
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # pour importer exemples/slack.py
import slack

maintenant = int(time.time())
mention = os.getenv("SLACK_MENTION_ID", "").strip()

# 1. Format « mrkdwn » de Slack (attention : *gras* avec UNE étoile, pas deux)
slack.envoyer(
    "*Gras*  _italique_  ~barré~  `code`\n"
    "> Citation : utile pour mettre en avant un résumé\n"
    "• Liste à puces (caractère •)\n"
    "<https://example.com|Lien avec un libellé>\n"
    # La date s'affiche dans le fuseau horaire et la langue de chaque lecteur.
    f"Date localisée : <!date^{maintenant}^{{date_short_pretty}} à {{time}}|{maintenant}>\n"
    + (f"Mention : <@{mention}>\n" if mention else "Mention : <@ID_MEMBRE> (renseignez SLACK_MENTION_ID)\n")
    + "Emojis : :white_check_mark: :warning: :rotating_light: ou directement ✅ ⚠️ 🚨\n"
    "```Bloc de code : traces d'erreur, tableaux alignés…\nKeyError: 'query'```"
)

# 2. Bloc « markdown » : markdown standard (**gras**, [lien](url)), pratique pour du texte écrit par une IA
slack.envoyer("Bloc markdown", blocks=[{
    "type": "markdown",
    "text": "**Bloc markdown standard**\n- [lien](https://example.com)\n- `code`\n- *italique*",
}])

# 3. Barre de couleur à gauche (champ « attachments »)
slack.envoyer("Barres de couleur", attachments=[
    {"color": "#2EB67D", "text": "Vert : succès"},
    {"color": "#ECB22E", "text": "Jaune : avertissement"},
    {"color": "#E01E5A", "text": "Rouge : erreur"},
])

print("3 messages envoyés")
