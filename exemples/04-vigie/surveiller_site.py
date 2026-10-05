"""Surveille la disponibilité et le temps de réponse de sites ou d'API.

    python exemples/04-vigie/surveiller_site.py

À lancer régulièrement (toutes les 5 minutes par exemple, voir le README du dossier).
Grâce à vigie.signaler, on n'est prévenu qu'au changement : panne, lenteur, puis retour à la normale.
"""
import time

import requests

from vigie import signaler

# Ce qu'on surveille : nom affiché → URL. Le deuxième site est volontairement en panne pour la démo.
SITES = {
    "Site example.com": "https://example.com",
    "Site de démo en panne": "https://site-de-demo.invalid",
}
LENT_AU_DELA = 3.0   # secondes : au-delà, avertissement
TIMEOUT = 15         # secondes : au-delà, on considère le site en panne


def verifier(nom, url):
    debut = time.monotonic()
    try:
        r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "vigie-slack"})
        duree = time.monotonic() - debut
        champs = {"URL": url, "Code HTTP": str(r.status_code), "Temps de réponse": f"{duree:.2f} s"}
        if r.status_code >= 500:
            return signaler(f"site:{url}", "critique", nom, "Le serveur renvoie une erreur", champs, lien=url)
        if r.status_code >= 400:
            return signaler(f"site:{url}", "erreur", nom, "La page renvoie une erreur", champs, lien=url)
        if duree > LENT_AU_DELA:
            return signaler(f"site:{url}", "avertissement", nom, "Le site répond lentement", champs, lien=url)
        return signaler(f"site:{url}", "ok", nom, champs=champs, lien=url)
    except requests.RequestException as exc:
        return signaler(f"site:{url}", "critique", nom, "Le site ne répond pas",
                        {"URL": url, "Erreur": type(exc).__name__}, lien=url)


if __name__ == "__main__":
    for nom, url in SITES.items():
        envoye = verifier(nom, url)
        print(f"{nom:28} {'→ message envoyé' if envoye else 'pas de changement'}")
