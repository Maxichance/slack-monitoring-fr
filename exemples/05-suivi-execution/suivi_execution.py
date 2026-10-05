"""Suivi d'exécution d'un script ou d'un pipeline : UN message par exécution dans le canal.

    python exemples/05-suivi-execution/suivi_execution.py           # exécution réussie
    python exemples/05-suivi-execution/suivi_execution.py --echec   # échec simulé à l'étape 3

Rendu dans Slack :
    canal : ⏳ Mon projet · démarré 06:00 · ✅✅⏳⬜ 2/4        ← mis à jour en direct
            ✅ Mon projet · 06:00 → 06:04 · ✅✅✅✅ 4/4 OK
    fil   : une réponse par étape (durée, résumé, trace d'erreur), log complet joint si échec.

En cas d'échec, le bilan est aussi publié dans le canal. Un succès ne génère pas de message supplémentaire.

À réutiliser :
    with Execution("Mon projet", ["Extraction", "Export"]) as run:
        with run.etape("Extraction") as e:
            lignes = extraire()
            e["resume"] = f"{len(lignes)} lignes"
"""
import socket
import sys
import time
import traceback
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # pour importer exemples/slack.py
import slack


def hms(secondes):
    s = int(round(secondes))
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


class Execution:
    def __init__(self, projet, etapes):
        self.projet = projet
        self.etapes = list(etapes)
        self.icones = ["⬜"] * len(self.etapes)
        self.run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.journal = []      # copie locale des événements, jointe en cas d'échec
        self.echecs = []
        self.ts = None

    # --- message principal -------------------------------------------------
    def _ligne(self, icone, fin=""):
        faites = sum(i in ("✅", "⚠️") for i in self.icones)
        return (f"{icone} *{self.projet}* · run `{self.run_id}` · {self.heure_debut}{fin} · "
                f"{''.join(self.icones)} {faites}/{len(self.etapes)}")

    def _noter(self, texte):
        self.journal.append(f"[{datetime.now():%H:%M:%S}] {texte}")
        print(texte)

    def __enter__(self):
        self.t0 = time.monotonic()
        self.heure_debut = datetime.now().strftime("%H:%M")
        self.ts = slack.envoyer(self._ligne("⏳", " (démarré)"))
        slack.envoyer(f"Démarrage sur `{socket.gethostname()}` · {len(self.etapes)} étapes prévues", fil=self.ts)
        self._noter(f"Démarrage de {self.projet} ({len(self.etapes)} étapes)")
        return self

    # --- étapes -------------------------------------------------------------
    @contextmanager
    def etape(self, nom):
        i = self.etapes.index(nom)
        numero = f"Étape {i + 1}/{len(self.etapes)} · {nom}"
        self.icones[i] = "⏳"
        slack.modifier(self.ts, self._ligne("⏳", " (en cours)"))
        self._noter(f"{numero} : début")
        infos = {"resume": "", "avertissement": ""}   # à remplir par le code de l'étape
        debut = time.monotonic()
        try:
            yield infos
        except BaseException as exc:
            self.icones[i] = "❌"
            self.echecs.append(nom)
            trace = traceback.format_exc()
            self._noter(f"{numero} : ÉCHEC\n{trace}")
            fin_trace = "\n".join(trace.strip().splitlines()[-15:])
            slack.envoyer(f"❌ `{numero}` échec après {hms(time.monotonic() - debut)}\n"
                          f"*{type(exc).__name__}* : {exc}\n```{fin_trace}```", fil=self.ts)
            raise   # on ne change pas le comportement du programme
        duree = hms(time.monotonic() - debut)
        if infos["avertissement"]:
            self.icones[i] = "⚠️"
            texte = f"⚠️ `{numero}` · {duree} · {infos['avertissement']}"
        else:
            self.icones[i] = "✅"
            texte = f"✅ `{numero}` · {duree}" + (f" · {infos['resume']}" if infos["resume"] else "")
        self._noter(texte)
        slack.envoyer(texte, fil=self.ts)

    # --- bilan --------------------------------------------------------------
    def __exit__(self, type_exc, exc, tb):
        duree = hms(time.monotonic() - self.t0)
        fin = f" → {datetime.now():%H:%M}"
        if type_exc is KeyboardInterrupt and not self.echecs:
            self.echecs.append("interrompu (Ctrl+C)")
        self.icones = ["⏭️" if i in ("⬜", "⏳") else i for i in self.icones]
        faites = sum(i in ("✅", "⚠️") for i in self.icones)

        if self.echecs or type_exc:
            slack.modifier(self.ts, self._ligne("❌", fin) + f" · échec : *{', '.join(self.echecs)}*")
            slack.joindre_fichier("\n".join(self.journal), f"{self.run_id}.log", "Log complet", fil=self.ts)
            slack.envoyer(f"❌ *Bilan {self.projet}* · {faites}/{len(self.etapes)} étapes OK · durée {duree}"
                          f" · échec : *{', '.join(self.echecs)}*", fil=self.ts, aussi_dans_canal=True)
        else:
            slack.modifier(self.ts, self._ligne("✅", fin) + f" OK · {duree}")
            slack.envoyer(f"✅ *Bilan* · {faites}/{len(self.etapes)} étapes OK · durée {duree}", fil=self.ts)
        return False   # l'exception éventuelle continue son chemin


if __name__ == "__main__":
    echec = "--echec" in sys.argv
    try:
        with Execution("Démo suivi d'exécution", ["Chargement", "Extraction", "Transformation", "Export"]) as run:
            with run.etape("Chargement") as e:
                time.sleep(1)
                e["resume"] = "3 sources configurées"
            with run.etape("Extraction") as e:
                time.sleep(2)
                e["resume"] = "182 340 lignes"
            with run.etape("Transformation") as e:
                time.sleep(1)
                if echec:
                    ligne = {"id": 1}
                    ligne["query"]   # KeyError volontaire
                e["resume"] = "27 éléments détectés"
            with run.etape("Export") as e:
                time.sleep(1)
                e["avertissement"] = "0 ligne exportée (fichier vide)"
    except KeyError:
        print("Échec simulé : voir le message dans Slack")
