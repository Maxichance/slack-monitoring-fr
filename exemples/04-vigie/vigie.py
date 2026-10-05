"""Mémoire d'état de la vigie : on n'alerte que lorsque l'état d'une surveillance change.

Répéter la même alerte à chaque vérification la rend inutile. La règle appliquée :

    OK      → problème  : alerte (avertissement, erreur ou critique)
    problème → problème : silence (sauf un rappel toutes les RAPPEL_APRES)
    problème → OK       : message « ✅ Rétabli après 23 min »
    OK      → OK        : silence

L'état de chaque surveillance est mémorisé dans etat_vigie.json, à côté de ce fichier
(ignoré par git). Supprimez ce fichier pour tout remettre à zéro.
"""
import json
import sys
import time
from pathlib import Path

DOSSIER_EXEMPLES = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DOSSIER_EXEMPLES))                  # exemples/slack.py
sys.path.insert(0, str(DOSSIER_EXEMPLES / "03-alertes"))   # exemples/03-alertes/alertes.py
from alertes import alerte  # noqa: E402

FICHIER_ETAT = Path(__file__).with_name("etat_vigie.json")
RAPPEL_APRES = 6 * 3600  # secondes : relance si le problème dure toujours
GRAVITE = {"ok": 0, "avertissement": 1, "erreur": 2, "critique": 3}


def _charger():
    try:
        return json.loads(FICHIER_ETAT.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}


def _sauver(etats):
    FICHIER_ETAT.write_text(json.dumps(etats, ensure_ascii=False, indent=2), encoding="utf-8")


def duree_lisible(secondes):
    secondes = int(secondes)
    if secondes < 60:
        return f"{secondes} s"
    if secondes < 3600:
        return f"{secondes // 60} min"
    if secondes < 86400:
        return f"{secondes // 3600} h {secondes % 3600 // 60:02d}"
    return f"{secondes // 86400} j {secondes % 86400 // 3600} h"


def signaler(cle, statut, titre, details="", champs=None, lien=None, source="vigie", canal=None):
    """Enregistre le statut d'une surveillance et prévient Slack si nécessaire.

    cle    : identifiant stable de la surveillance (ex. "site:example.com")
    statut : "ok" | "avertissement" | "erreur" | "critique"
    titre  : ce qui est surveillé, en clair (ex. "Site example.com")
    canal  : ID d'un autre canal que SLACK_CHANNEL_ID (facultatif)
    Renvoie True si un message a été envoyé.
    """
    maintenant = time.time()
    etats = _charger()
    precedent = etats.get(cle, {"statut": "ok", "depuis": maintenant, "dernier_envoi": 0})

    if statut == precedent["statut"]:
        # Pas de changement : silence, sauf rappel périodique si le problème dure.
        if statut != "ok" and maintenant - precedent.get("dernier_envoi", 0) >= RAPPEL_APRES:
            alerte(statut, f"Toujours en cours : {titre}",
                   f"{details}\nProblème en cours depuis {duree_lisible(maintenant - precedent['depuis'])}",
                   champs=champs, lien=lien, source=source, canal=canal)
            precedent["dernier_envoi"] = maintenant
            etats[cle] = precedent
            _sauver(etats)
            return True
        return False

    if statut == "ok":
        alerte("succes", f"Rétabli : {titre}",
               f"Retour à la normale après {duree_lisible(maintenant - precedent['depuis'])}",
               champs=champs, lien=lien, source=source, canal=canal)
    else:
        aggravation = GRAVITE[statut] > GRAVITE[precedent["statut"]] and precedent["statut"] != "ok"
        alerte(statut, ("Aggravation : " if aggravation else "") + titre, details,
               champs=champs, lien=lien, source=source, canal=canal)

    # On garde la date de début du problème si on passe seulement d'un niveau à l'autre.
    debut = precedent["depuis"] if precedent["statut"] != "ok" and statut != "ok" else maintenant
    etats[cle] = {"statut": statut, "depuis": debut, "dernier_envoi": maintenant}
    _sauver(etats)
    return True
