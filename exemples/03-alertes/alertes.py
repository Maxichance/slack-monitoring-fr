"""Cinq niveaux d'alerte, chacun avec son emoji et sa couleur.

    python exemples/03-alertes/alertes.py

À réutiliser tel quel :  from alertes import alerte
    alerte("erreur", "Export impossible", "Le serveur FTP ne répond pas",
           champs={"Serveur": "ftp.example.com", "Tentatives": "3"})

Seul le niveau « critique » mentionne quelqu'un (SLACK_MENTION_ID dans le .env), pour
que les mentions restent réservées aux urgences.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # pour importer exemples/slack.py
import slack

NIVEAUX = {
    #  niveau          emoji  couleur    libellé
    "info":          ("ℹ️", "#1D9BD1", "Info"),
    "succes":        ("✅", "#2EB67D", "Succès"),
    "avertissement": ("⚠️", "#ECB22E", "Avertissement"),
    "erreur":        ("❌", "#E01E5A", "Erreur"),
    "critique":      ("🚨", "#8B0000", "CRITIQUE"),
}


def alerte(niveau, titre, details="", champs=None, lien=None, source=None, fil=None, canal=None):
    """Envoie une alerte formatée. Renvoie le ts du message.

    niveau  : info | succes | avertissement | erreur | critique
    champs  : dict affiché en colonnes (ex. {"Serveur": "web-01", "Durée": "12 s"})
    lien    : URL ouverte par un bouton « Voir le détail »
    source  : nom du projet / de la sonde, affiché en petit en bas
    canal   : ID d'un autre canal que SLACK_CHANNEL_ID (ex. un canal dédié aux alertes)
    """
    emoji, couleur, libelle = NIVEAUX[niveau]
    mention = os.getenv("SLACK_MENTION_ID", "").strip()
    entete = f"{emoji} *{libelle} · {titre}*"
    if niveau == "critique" and mention:
        entete += f"  <@{mention}>"

    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": entete + (f"\n{details}" if details else "")}}]
    if champs:
        blocks.append({"type": "section", "fields": [
            {"type": "mrkdwn", "text": f"*{k}*\n{v}"} for k, v in list(champs.items())[:10]]})
    if lien:
        blocks.append({"type": "actions", "elements": [
            {"type": "button", "text": {"type": "plain_text", "text": "Voir le détail"}, "url": lien}]})
    if source:
        blocks.append({"type": "context", "elements": [{"type": "mrkdwn", "text": source}]})

    # Le texte simple sert aux notifications (téléphone, bureau) : il doit se suffire à lui-même.
    return slack.envoyer(f"{emoji} {libelle} · {titre}", attachments=[{"color": couleur, "blocks": blocks}],
                         fil=fil, canal=canal)


if __name__ == "__main__":
    alerte("info", "Démarrage de la collecte", "3 sources à traiter", source="démo · exemples/03-alertes")
    alerte("succes", "Collecte terminée", champs={"Lignes": "182 340", "Durée": "00:03:41"})
    alerte("avertissement", "Source partielle", "La source B n'a renvoyé que 40 % des données habituelles",
           champs={"Attendu": "~50 000", "Reçu": "19 870"})
    alerte("erreur", "Export impossible", "Le serveur ne répond pas après 3 tentatives",
           champs={"Serveur": "ftp.example.com", "Code": "Timeout"}, lien="https://example.com")
    alerte("critique", "Site inaccessible", "La page d'accueil renvoie une erreur 503 depuis 10 minutes",
           champs={"URL": "https://example.com", "Depuis": "10 min"}, lien="https://example.com")
    print("5 alertes envoyées")
