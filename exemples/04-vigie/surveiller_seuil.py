"""Surveille une valeur et alerte quand elle franchit un seuil (puis quand elle revient).

    python exemples/04-vigie/surveiller_seuil.py          # vraie mesure : espace disque
    python exemples/04-vigie/surveiller_seuil.py --demo   # simulation : 55 → 82 → 93 → 95 → 40 %

Remplacez la mesure par ce qui vous intéresse : nombre de lignes reçues, taux d'erreur,
stock d'un produit, prix d'un concurrent, nombre de commandes de l'heure…
"""
import shutil
import sys
import time
from pathlib import Path

from vigie import signaler


def verifier_seuil(cle, nom, valeur, avertissement, critique, unite="", plus_haut_est_pire=True):
    """Compare une valeur à deux seuils et transmet le statut à la vigie."""
    def depasse(seuil):
        return valeur >= seuil if plus_haut_est_pire else valeur <= seuil

    if depasse(critique):
        statut = "critique"
    elif depasse(avertissement):
        statut = "avertissement"
    else:
        statut = "ok"
    sens = "≥" if plus_haut_est_pire else "≤"
    champs = {"Valeur": f"{valeur:g} {unite}".strip(),
              "Seuils": f"avertissement {sens} {avertissement:g}, critique {sens} {critique:g} {unite}".strip()}
    details = f"{nom} : *{valeur:g} {unite}*".strip()
    return signaler(cle, statut, nom, details, champs, source="vigie · seuils")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        for valeur in (55, 82, 93, 95, 40):
            envoye = verifier_seuil("demo:disque", "Disque du serveur de démo", valeur, 80, 90, "%")
            print(f"valeur {valeur:>3} % → {'message envoyé' if envoye else 'silence'}")
            time.sleep(1.5)
    else:
        usage = shutil.disk_usage(Path.cwd().anchor or "/")
        pourcentage = round(usage.used / usage.total * 100, 1)
        envoye = verifier_seuil("disque:local", "Espace disque utilisé", pourcentage, 80, 90, "%")
        print(f"Disque utilisé : {pourcentage} % → {'message envoyé' if envoye else 'pas de changement'}")
