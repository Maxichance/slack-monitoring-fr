# Utilisation depuis BigQuery

Envoyer des messages Slack depuis un notebook Python de BigQuery Studio (Colab Enterprise) : installation des librairies, stockage du jeton, planification et points d'attention.

[Retour au README](../README.md)

1. [Installer les librairies](#1-installer-les-librairies)
2. [Stocker le jeton dans Secret Manager](#2-stocker-le-jeton-dans-secret-manager)
3. [Envoyer un message depuis le notebook](#3-envoyer-un-message-depuis-le-notebook)
4. [Envoyer le résultat d'une requête](#4-envoyer-le-résultat-dune-requête)
5. [Planifier le notebook](#5-planifier-le-notebook)
6. [Points d'attention](#6-points-dattention)

## 1. Installer les librairies

Les librairies Slack ne sont pas présentes par défaut dans l'environnement d'exécution. Dans la première cellule du notebook :

```python
%pip install --quiet slack_sdk google-cloud-secret-manager
```

- `slack_sdk` : client officiel Slack (`from slack_sdk import WebClient`). Il est inutile si vous utilisez [`exemples/slack.py`](../exemples/slack.py), qui ne dépend que de `requests`, déjà disponible.
- `google-cloud-secret-manager` : lecture du jeton dans Secret Manager (section 2).
- `google-cloud-bigquery`, `pandas` et `matplotlib` sont en général déjà installés.

Si un import échoue juste après l'installation, redémarrez l'environnement d'exécution (menu **Exécution**, **Redémarrer la session**) puis relancez les cellules.

## 2. Stocker le jeton dans Secret Manager

Un notebook est partagé, versionné et parfois exporté : le jeton ne doit pas y être écrit en clair, et il n'y a pas de fichier `.env`. Google Cloud Secret Manager est l'emplacement prévu pour ce type de valeur.

Création du secret et attribution du droit de lecture, une seule fois, depuis Cloud Shell :

```bash
printf "xoxb-..." | gcloud secrets create slack-bot-token --data-file=-

gcloud secrets add-iam-policy-binding slack-bot-token \
  --member="serviceAccount:COMPTE@PROJET.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Le droit `roles/secretmanager.secretAccessor` doit être accordé à l'identité qui exécute le notebook : votre compte pour une exécution manuelle, le compte de service choisi pour une exécution planifiée (section 5).

Lecture dans le notebook :

```python
from google.cloud import secretmanager

def lire_secret(nom, projet="ID_DU_PROJET"):
    client = secretmanager.SecretManagerServiceClient()
    chemin = f"projects/{projet}/secrets/{nom}/versions/latest"
    return client.access_secret_version(name=chemin).payload.data.decode("utf-8")
```

## 3. Envoyer un message depuis le notebook

### Avec `exemples/slack.py`

`slack.py` lit sa configuration dans les variables d'environnement : il suffit de les définir avant de l'importer. Le fichier peut être téléchargé depuis le dépôt, ou collé tel quel dans une cellule.

```python
import os
os.environ["SLACK_BOT_TOKEN"] = lire_secret("slack-bot-token")
os.environ["SLACK_CHANNEL_ID"] = "C0123456789"

!wget -q -O slack.py https://raw.githubusercontent.com/Maxichance/slack-monitoring-fr/main/exemples/slack.py
import slack

slack.envoyer("Test depuis BigQuery")
```

### Avec `slack_sdk`

```python
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token=lire_secret("slack-bot-token"))
try:
    client.chat_postMessage(channel="C0123456789", text="Test depuis BigQuery")
except SlackApiError as e:
    print("Erreur Slack :", e.response["error"])
```

## 4. Envoyer le résultat d'une requête

Exemple : un résumé en colonnes et un CSV joint, à partir d'une requête sur un jeu de données public.

```python
from google.cloud import bigquery

requete = """
SELECT name, SUM(number) AS total
FROM `bigquery-public-data.usa_names.usa_1910_current`
WHERE year = 2020
GROUP BY name
ORDER BY total DESC
LIMIT 10
"""
df = bigquery.Client().query(requete).to_dataframe()

blocs = [
    {"type": "header", "text": {"type": "plain_text", "text": "Top 10 des prénoms (2020)"}},
    {"type": "section", "fields": [
        {"type": "mrkdwn", "text": f"*{ligne.name}*\n{ligne.total:,}".replace(",", " ")}
        for ligne in df.head(10).itertuples()]},
]
ts = slack.envoyer("Top 10 des prénoms (2020)", blocks=blocs)
slack.joindre_fichier(df.to_csv(index=False, sep=";").encode("utf-8-sig"), "top_prenoms.csv", fil=ts)
```

Un bloc `section` accepte 10 champs au maximum. Pour plus de lignes, utilisez le bloc `table` ([`exemples/06-tableaux`](../exemples/06-tableaux/)) ou un fichier joint.

## 5. Planifier le notebook

Dans BigQuery Studio, un notebook peut être exécuté selon un calendrier (option **Planifier** du notebook). L'exécution planifiée se fait avec un compte de service :

- ce compte doit avoir le droit de lecture sur le secret (section 2) ;
- il doit aussi pouvoir lire les tables interrogées et lancer des requêtes (par exemple `roles/bigquery.dataViewer` et `roles/bigquery.jobUser`), en plus des droits demandés par la planification elle-même (voir la documentation Google Cloud sur la planification des notebooks) ;
- la cellule d'installation (`%pip install`) doit rester en tête du notebook, car chaque exécution démarre dans un environnement neuf.

Les fonctions de `slack.py` ne lèvent pas d'exception en cas d'erreur Slack. Pour qu'une exécution planifiée soit marquée en échec quand l'envoi échoue, testez la valeur renvoyée :

```python
if slack.envoyer("Rapport du jour") is None:
    raise RuntimeError("Envoi Slack impossible")
```

## 6. Points d'attention

**Accès réseau.** Les environnements d'exécution des notebooks ont accès à Internet par défaut. Si l'organisation restreint les sorties réseau (VPC Service Controls, pare-feu), les domaines `slack.com` et `files.slack.com` doivent être autorisés, ainsi que `quickchart.io` si vous l'utilisez.

**Confidentialité des graphiques.** Les données issues de BigQuery sont souvent internes. QuickChart envoie les valeurs à un service externe et produit une image publique. Préférez un graphique matplotlib envoyé comme fichier ([`graphique_prive.py`](../exemples/07-graphiques/graphique_prive.py)) : les données restent entre Google Cloud et Slack.

**Limite de 50 blocs par message.** Un rapport qui génère plusieurs blocs par élément (texte, images, légende, séparateur) atteint vite cette limite. Slack renvoie alors `invalid_blocks`, la même erreur qu'une image inaccessible. Avant de retirer les images en guise de solution de repli, vérifiez le nombre de blocs (`len(blocks)`). Au-delà de 50, découpez le rapport en plusieurs messages, par exemple un message principal et le détail dans son fil.

**Menus déroulants.** Un `static_select` placé dans un message s'affiche sans configuration particulière. En revanche, choisir une option envoie un événement à l'application : sans interactivité configurée (URL de requête et serveur), Slack signale une erreur. Pour une liste purement informative, préférez du texte ou un bloc `context`.

**Librairies tierces.** Les librairies qui interrogent des services non officiels, par exemple `pytrends` pour Google Trends, sont régulièrement bloquées (erreurs 429), en particulier depuis des serveurs. Elles ne sont pas nécessaires pour Slack : installez-les seulement si votre script les utilise, et prévoyez un rapport qui reste lisible sans ces données.
