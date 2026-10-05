"""Programmer un message, et afficher un message temporaire qui disparaît.

    python exemples/10-messages-programmes/messages_programmes.py

- chat.scheduleMessage : Slack envoie le message à l'heure dite, même si votre script est arrêté
  (rappel, relance, « bonne semaine » du lundi…). Jusqu'à 120 jours à l'avance.
- chat.update + chat.delete : un message « en cours… » qui disparaît une fois le travail fini.
"""
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # pour importer exemples/slack.py
import slack

if __name__ == "__main__":
    # 1. Message programmé dans 2 minutes
    dans_2_minutes = datetime.now() + timedelta(minutes=2)
    if slack.programmer(f"Message programmé à {dans_2_minutes:%H:%M} (chat.scheduleMessage)",
                        dans_2_minutes.timestamp()):
        print(f"Message programmé pour {dans_2_minutes:%H:%M}")

    # 2. Message temporaire : affiché pendant le travail, puis supprimé
    ts = slack.envoyer("⏳ Traitement en cours… (ce message va disparaître)")
    for pourcentage in (25, 50, 75, 100):
        time.sleep(1.5)
        slack.modifier(ts, f"⏳ Traitement en cours… {pourcentage} % (ce message va disparaître)")
    time.sleep(2)
    slack.supprimer(ts)
    print("Message temporaire affiché puis supprimé")
