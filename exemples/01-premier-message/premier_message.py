"""Vérifie que tout est bien branché : envoie un message de test dans le canal.

    python exemples/01-premier-message/premier_message.py
"""
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # pour importer exemples/slack.py
import slack

ts = slack.envoyer(f"Test de connexion depuis `{socket.gethostname()}` :white_check_mark:")

if ts:
    print(f"Message envoyé. Canal : {slack.lien_canal() or slack.CANAL}")
else:
    print("Échec de l'envoi : voir l'erreur ci-dessus et la section Dépannage de docs/installation.md")
    sys.exit(1)
