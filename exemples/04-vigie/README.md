# 04 · Vigie

Surveillances qui n'envoient un message que lorsque l'état change : apparition d'un problème, aggravation, retour à la normale. Si un problème dure, un rappel est envoyé toutes les 6 heures (réglable dans `vigie.py`).

[Retour aux exemples](../README.md)

```
🚨 CRITIQUE · Site de démo en panne                 début de la panne
                                                    aucun message pendant la panne
✅ Succès · Rétabli : Site de démo en panne
   Retour à la normale après 23 min                 fin de la panne
```

## Fichiers

| Fichier | Rôle | Démonstration |
|---|---|---|
| [`vigie.py`](vigie.py) | Mémorise l'état de chaque surveillance (`etat_vigie.json`) et décide s'il faut envoyer un message | |
| [`surveiller_site.py`](surveiller_site.py) | Disponibilité, code HTTP et temps de réponse de sites ou d'API | `python surveiller_site.py` |
| [`surveiller_seuil.py`](surveiller_seuil.py) | Valeur qui franchit un seuil d'avertissement ou critique (disque, volumes, taux d'erreur, stock…) | `python surveiller_seuil.py --demo` |
| [`detecter_changement.py`](detecter_changement.py) | Contenu modifié (page, API, export), avec les lignes ajoutées et retirées | `python detecter_changement.py --demo` |
| [`surveiller_fraicheur.py`](surveiller_fraicheur.py) | Fichiers qui ne sont plus mis à jour (job planifié arrêté) | `python surveiller_fraicheur.py --demo` |

Pour réinitialiser les états, supprimez `etat_vigie.json` et `etat_contenus.json`.

## Planification

Les surveillances doivent être lancées à intervalle régulier.

**Windows, Planificateur de tâches** (toutes les 5 minutes) :

```powershell
schtasks /Create /TN "Vigie sites" /SC MINUTE /MO 5 /TR "C:\chemin\vers\python.exe C:\chemin\vers\exemples\04-vigie\surveiller_site.py"
```

**macOS, Linux, cron** (`crontab -e`) :

```cron
*/5 * * * *  cd /chemin/vers/le/depot && python exemples/04-vigie/surveiller_site.py >> vigie.log 2>&1
0 8 * * 1-5  cd /chemin/vers/le/depot && python exemples/09-rapport-quotidien/rapport_quotidien.py
```

**GitHub Actions** : un workflow déclenché par `on: schedule` (par exemple `cron: "*/15 * * * *"`), avec `SLACK_BOT_TOKEN` dans les secrets du dépôt. Sans cache, le fichier `etat_vigie.json` n'est pas conservé d'une exécution à l'autre : un serveur reste préférable pour des vérifications fréquentes.

## Recommandations

- Envoyez un rapport quotidien même quand tout va bien (voir [09-rapport-quotidien](../09-rapport-quotidien/)) : son absence signale que la surveillance elle-même est arrêtée.
- Réservez les mentions au niveau critique (variable `SLACK_MENTION_ID`).
- Si le volume augmente, séparez les sujets dans plusieurs canaux (par exemple `#vigie-sites` et `#vigie-donnees`) avec le paramètre `canal="C…"` de `signaler(...)`.
- Pour la détection de changement, comparez le texte ou la valeur utile plutôt que le HTML brut : une date ou une publicité qui change suffirait à déclencher une alerte.
