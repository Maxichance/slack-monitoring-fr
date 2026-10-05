"""Mini-client Slack partagé par tous les exemples.

Une seule dépendance HTTP (requests), aucun SDK Slack. Copiez ce fichier dans votre
projet : il suffit pour envoyer, modifier, programmer et supprimer des messages, et
pour joindre des fichiers.

Configuration lue dans les variables d'environnement, ou dans un fichier .env si
python-dotenv est installé (voir .env.example à la racine du dépôt) :
    SLACK_BOT_TOKEN, SLACK_CHANNEL_ID, SLACK_WORKSPACE_URL, SLACK_ENABLED

Une erreur Slack ne fait jamais planter le programme : elle est affichée dans la
console et la fonction renvoie None.
"""
import os
import time
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # notebook, CI… : les variables d'environnement suffisent
    load_dotenv = None

if load_dotenv:
    if "__file__" in globals():  # absent quand le code est collé dans une cellule de notebook
        load_dotenv(Path(__file__).resolve().parent.parent / ".env")  # .env à la racine du dépôt
    load_dotenv()  # .env du dossier courant

API = "https://slack.com/api/"
TOKEN = os.getenv("SLACK_BOT_TOKEN", "").strip()
# Accepte un ID (C0123…) ou une URL complète de canal : on garde la dernière partie.
CANAL = os.getenv("SLACK_CHANNEL_ID", "").strip().rstrip("/").split("/")[-1]
WORKSPACE_URL = os.getenv("SLACK_WORKSPACE_URL", "").strip().rstrip("/")
ACTIF = os.getenv("SLACK_ENABLED", "true").strip().lower() not in ("false", "0", "non", "no")

if ACTIF and not (TOKEN and CANAL):
    print("[slack] SLACK_BOT_TOKEN ou SLACK_CHANNEL_ID manquant : envois désactivés")
    ACTIF = False

LIMITE_TEXTE = 3500


def appeler(methode, json=None, data=None):
    """Appelle une méthode de l'API Slack. Renvoie la réponse (dict) ou None en cas d'échec."""
    if not ACTIF:
        return None
    for tentative in range(2):
        try:
            r = requests.post(API + methode, headers={"Authorization": f"Bearer {TOKEN}"},
                              json=json, data=data, timeout=10)
        except requests.RequestException as exc:
            print(f"[slack] {methode} : erreur réseau ({exc})")
            return None
        if r.status_code == 429 and tentative == 0:  # quota dépassé : on attend puis on réessaie une fois
            time.sleep(int(r.headers.get("Retry-After", "1")))
            continue
        reponse = r.json()
        # Slack répond HTTP 200 même en cas d'erreur : seul le champ "ok" fait foi.
        if not reponse.get("ok"):
            print(f"[slack] {methode} : {reponse.get('error')}")
            return None
        return reponse
    return None


def _tronquer(texte):
    return texte if len(texte) <= LIMITE_TEXTE else texte[:LIMITE_TEXTE - 20] + "\n… (tronqué)"


def envoyer(texte, blocks=None, attachments=None, fil=None, aussi_dans_canal=False, canal=None):
    """Envoie un message. Renvoie son identifiant `ts` (utile pour le modifier ou y répondre).

    texte            : texte du message, aussi utilisé pour les notifications (obligatoire)
    blocks           : blocs Block Kit (mise en page riche)
    attachments      : pièces jointes « legacy » (barre de couleur à gauche)
    fil              : ts d'un message parent, pour répondre dans son fil
    aussi_dans_canal : avec `fil`, affiche aussi la réponse dans le canal
    """
    corps = {"channel": canal or CANAL, "text": _tronquer(texte)}
    if blocks:
        corps["blocks"] = blocks
    if attachments:
        corps["attachments"] = attachments
    if fil:
        corps["thread_ts"] = fil
        corps["reply_broadcast"] = aussi_dans_canal
    reponse = appeler("chat.postMessage", json=corps)
    return reponse["ts"] if reponse else None


def modifier(ts, texte, blocks=None, attachments=None, canal=None):
    """Remplace le contenu d'un message déjà envoyé par le bot."""
    if not ts:
        return None
    corps = {"channel": canal or CANAL, "ts": ts, "text": _tronquer(texte)}
    if blocks is not None:
        corps["blocks"] = blocks
    if attachments is not None:
        corps["attachments"] = attachments
    return appeler("chat.update", json=corps)


def supprimer(ts, canal=None):
    """Supprime un message envoyé par le bot."""
    return appeler("chat.delete", json={"channel": canal or CANAL, "ts": ts}) if ts else None


def programmer(texte, a_l_instant, fil=None, canal=None):
    """Programme un message pour plus tard. `a_l_instant` : timestamp Unix (secondes)."""
    corps = {"channel": canal or CANAL, "text": texte, "post_at": int(a_l_instant)}
    if fil:
        corps["thread_ts"] = fil
    return appeler("chat.scheduleMessage", json=corps)


def joindre_fichier(contenu, nom_fichier, titre=None, commentaire=None, fil=None, canal=None):
    """Envoie un fichier (bytes ou str) dans le canal ou dans un fil. Renvoie l'ID du fichier.

    Méthode actuelle de Slack en 3 temps (files.upload est obsolète). Droit requis : files:write.
    """
    if isinstance(contenu, str):
        contenu = contenu.encode("utf-8")
    etape1 = appeler("files.getUploadURLExternal", data={"filename": nom_fichier, "length": len(contenu)})
    if not etape1:
        return None
    try:
        requests.post(etape1["upload_url"], files={"file": (nom_fichier, contenu)}, timeout=60)
    except requests.RequestException as exc:
        print(f"[slack] envoi du fichier : erreur réseau ({exc})")
        return None
    corps = {"files": [{"id": etape1["file_id"], "title": titre or nom_fichier}],
             "channel_id": canal or CANAL}
    if commentaire:
        corps["initial_comment"] = commentaire
    if fil:
        corps["thread_ts"] = fil
    return etape1["file_id"] if appeler("files.completeUploadExternal", json=corps) else None


def lien_canal(canal=None):
    """Lien cliquable vers le canal (nécessite SLACK_WORKSPACE_URL)."""
    return f"{WORKSPACE_URL}/{canal or CANAL}" if WORKSPACE_URL else ""
