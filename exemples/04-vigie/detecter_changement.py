"""Veille : prévient quand un contenu change (page web, API, fichier, export…) et montre ce qui a changé.

    python exemples/04-vigie/detecter_changement.py --demo   # simule deux versions d'une liste de prix

Usage réel, par exemple sur une page ou une API :
    contenu = requests.get("https://example.com/tarifs", timeout=15).text
    surveiller_contenu("tarifs", "Page tarifs", contenu, lien="https://example.com/tarifs")

Conseil : surveillez une version « nettoyée » du contenu (texte utile, JSON trié) plutôt que
la page HTML brute, sinon la moindre date ou publicité déclenche une alerte.
"""
import difflib
import hashlib
import json
import sys
import time
from pathlib import Path

DOSSIER_EXEMPLES = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DOSSIER_EXEMPLES))
sys.path.insert(0, str(DOSSIER_EXEMPLES / "03-alertes"))
import slack  # noqa: E402
from alertes import alerte  # noqa: E402

FICHIER_ETAT = Path(__file__).with_name("etat_contenus.json")
MAX_LIGNES_DIFF = 12


def surveiller_contenu(cle, nom, contenu, lien=None):
    """Compare le contenu à la version précédente. Renvoie True si un changement a été signalé."""
    try:
        etats = json.loads(FICHIER_ETAT.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        etats = {}
    empreinte = hashlib.sha256(contenu.encode("utf-8")).hexdigest()
    precedent = etats.get(cle)
    etats[cle] = {"empreinte": empreinte, "contenu": contenu[:200_000], "vu_le": time.time()}
    FICHIER_ETAT.write_text(json.dumps(etats, ensure_ascii=False), encoding="utf-8")

    if precedent is None:
        print(f"{nom} : première lecture, version de référence enregistrée")
        return False
    if precedent["empreinte"] == empreinte:
        return False

    diff = [ligne for ligne in difflib.unified_diff(
        precedent["contenu"].splitlines(), contenu.splitlines(), lineterm="", n=0)
        if ligne[:1] in "+-" and not ligne.startswith(("+++", "---"))]
    ajouts = sum(ligne.startswith("+") for ligne in diff)
    retraits = len(diff) - ajouts
    apercu = "\n".join(diff[:MAX_LIGNES_DIFF]) + ("\n…" if len(diff) > MAX_LIGNES_DIFF else "")

    ts = alerte("info", f"Changement détecté : {nom}", f"```{apercu}```",
                champs={"Lignes ajoutées": str(ajouts), "Lignes retirées": str(retraits)},
                lien=lien, source="vigie · détection de changement")
    if len(diff) > MAX_LIGNES_DIFF and ts:  # diff complet joint dans le fil s'il est long
        slack.joindre_fichier("\n".join(diff), f"{cle}_diff.txt", "Différences complètes", fil=ts)
    return True


if __name__ == "__main__":
    if "--demo" not in sys.argv:
        print("Lancez avec --demo, ou importez surveiller_contenu dans votre script.")
        sys.exit(0)
    version_1 = "Produit A : 19,99 €\nProduit B : 34,90 €\nProduit C : 9,99 €"
    version_2 = "Produit A : 17,99 €\nProduit B : 34,90 €\nProduit C : 9,99 €\nProduit D : 24,90 €"
    surveiller_contenu("demo:prix", "Liste de prix (démo)", version_1)
    surveiller_contenu("demo:prix", "Liste de prix (démo)", version_1)   # identique : silence
    envoye = surveiller_contenu("demo:prix", "Liste de prix (démo)", version_2, lien="https://example.com")
    print("Changement signalé" if envoye else "Aucun changement")
