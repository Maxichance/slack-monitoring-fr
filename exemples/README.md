# Exemples

Scripts Python courts et commentés. Chacun fonctionne seul et envoie une démonstration dans le canal configuré.

[Retour au README](../README.md)

## Lancer un exemple

Depuis la racine du dépôt, une fois le `.env` renseigné (voir l'[installation](../docs/installation.md)) :

```bash
pip install -r exemples/requirements.txt
python exemples/01-premier-message/premier_message.py
```

Faites les essais dans un canal de test plutôt que dans le canal qui reçoit les vraies alertes.

## Liste des exemples

| Dossier | Contenu | Fichiers |
|---|---|---|
| [`slack.py`](slack.py) | Mini-client partagé : envoyer, modifier, supprimer, programmer un message, joindre un fichier | |
| [01-premier-message](01-premier-message/) | Test de connexion | `premier_message.py`, `test_connexion.ps1`, `test_connexion.sh` |
| [02-mise-en-forme](02-mise-en-forme/) | Gras, liens, mentions, dates localisées, blocs de code, markdown, couleurs | `mise_en_forme.py` |
| [03-alertes](03-alertes/) | Cinq niveaux d'alerte avec couleur, champs et bouton | `alertes.py` |
| [04-vigie](04-vigie/) | Surveillance avec alerte au changement d'état : sites, seuils, contenus, fraîcheur des données | `vigie.py`, `surveiller_*.py`, `detecter_changement.py` |
| [05-suivi-execution](05-suivi-execution/) | Suivi d'un script étape par étape : message mis à jour en direct, détail dans le fil, log joint en cas d'échec | `suivi_execution.py` |
| [06-tableaux](06-tableaux/) | Trois façons d'afficher un tableau | `tableaux.py` |
| [07-graphiques](07-graphiques/) | Sparkline, QuickChart, graphique matplotlib | `sparkline.py`, `quickchart.py`, `graphique_prive.py` |
| [08-fichiers](08-fichiers/) | Log, CSV et fichier Excel joints | `fichiers.py` |
| [09-rapport-quotidien](09-rapport-quotidien/) | Rapport du matin assemblant chiffres clés, tendances et tableau | `rapport_quotidien.py` |
| [10-messages-programmes](10-messages-programmes/) | Message programmé, message temporaire | `messages_programmes.py` |

## Réutiliser dans un projet

1. Copiez `slack.py`, et si besoin `03-alertes/alertes.py` et `04-vigie/vigie.py`, à côté de votre code.
2. Ajoutez `requests` et `python-dotenv` aux dépendances du projet.
3. Importez les fonctions :

```python
import slack
from alertes import alerte

slack.envoyer("Bonjour")
alerte("erreur", "Export impossible", "Le serveur ne répond pas", champs={"Tentatives": "3"})
```

Les fonctions ne lèvent pas d'exception en cas d'erreur Slack : l'erreur est affichée dans la console et le programme continue.

## Imports entre dossiers

Les noms de dossiers commencent par un chiffre et ne peuvent donc pas être importés comme des modules Python. Chaque script ajoute le dossier `exemples/` au chemin d'import :

```python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
```

Cette ligne est inutile dans un projet où `slack.py` est placé à côté du code.
