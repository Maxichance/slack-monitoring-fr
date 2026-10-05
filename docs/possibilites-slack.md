# Possibilités de Slack

Ce que le bot peut envoyer, les librairies utiles, et les droits nécessaires. Chaque section renvoie vers l'exemple de code correspondant.

Sauf mention contraire, tout ce qui suit fonctionne avec un bot qui a les droits `chat:write`, `files:write` et `files:read`. La section 7 liste ce qui demande des droits supplémentaires.

Pour composer un message visuellement et récupérer son JSON, utilisez le [Block Kit Builder](https://app.slack.com/block-kit-builder).

[Retour au README](../README.md)

## 1. Mise en forme du texte

Exemple : [`02-mise-en-forme`](../exemples/02-mise-en-forme/)

| Possibilité | Syntaxe |
|---|---|
| Gras, italique, barré, code | `*gras*` `_italique_` `~barré~` `` `code` `` |
| Bloc de code (traces d'erreur, tableaux alignés) | trois accents graves avant et après le texte |
| Lien avec un libellé | `<https://example.com\|Ouvrir le tableau de bord>` |
| Mention d'une personne | `<@ID_MEMBRE>` (profil Slack, menu ⋮, *Copier l'ID du membre*) |
| Date affichée dans le fuseau horaire du lecteur | `<!date^1791205628^{date_short_pretty} à {time}\|texte de secours>` |
| Mini-courbe en texte (sparkline) | caractères `▁▂▃▄▅▆▇█` calculés à partir des valeurs |
| Barre de couleur à gauche du message | champ `attachments` avec `"color": "#2EB67D"` (vert) ou `"#E01E5A"` (rouge) |

## 2. Messages structurés (Block Kit)

Exemples : [`03-alertes`](../exemples/03-alertes/), [`06-tableaux`](../exemples/06-tableaux/), [`09-rapport-quotidien`](../exemples/09-rapport-quotidien/)

On passe un champ `blocks` (liste JSON) à `chat.postMessage`. Gardez toujours un champ `text` : c'est lui qui s'affiche dans les notifications.

| Bloc | Usage |
|---|---|
| `header` | Titre |
| `section` + `fields` | Chiffres clés sur deux colonnes (10 cases au maximum) |
| `context` | Ligne secondaire en petit (identifiant d'exécution, machine, source) |
| `divider` | Séparateur |
| `table` | Tableau. Un seul par message |
| `markdown` | Markdown standard (`**gras**`, liens, listes), pratique pour du texte généré |
| `image` | Graphique ou capture (voir section 3) |
| `button` avec `url` | Bouton qui ouvre un lien. Sans interactivité configurée sur l'application, Slack peut afficher un avertissement au clic |
| `static_select` | Menu déroulant. Il s'affiche sans configuration, mais choisir une option nécessite l'interactivité et un serveur (voir section 7), sinon Slack signale une erreur |

Limites : 50 blocs par message, 3 000 caractères par bloc de texte.

## 3. Graphiques

Exemples : [`07-graphiques`](../exemples/07-graphiques/)

| Méthode | Principe | Avantages | Inconvénients |
|---|---|---|---|
| **QuickChart** ([`quickchart.py`](../exemples/07-graphiques/quickchart.py)) | Une configuration [Chart.js](https://www.chartjs.org/) est envoyée à [quickchart.io](https://quickchart.io), qui renvoie l'URL d'une image à placer dans un bloc `image`. | Aucune installation, utilisable depuis n'importe quel langage. | Les données partent chez un service externe et l'image est publique : toute personne qui a l'URL peut la voir. |
| **Image générée en local** ([`graphique_prive.py`](../exemples/07-graphiques/graphique_prive.py)) | Le script dessine un PNG (matplotlib, plotly…) et l'envoie comme fichier. | Les données restent dans Slack, aucun service tiers. | Une librairie à installer. |
| **Sparkline** ([`sparkline.py`](../exemples/07-graphiques/sparkline.py)) | Des caractères `▁▂▃▄▅▆▇█` calculés à partir des valeurs. | Aucune dépendance, lisible dans une notification. | Tendance uniquement, sans axes. |

Pour des données internes ou sensibles (chiffre d'affaires, stocks, prix, données clients), utilisez l'image générée en local.

Avec QuickChart, vérifiez que l'URL renvoie bien une image avant l'envoi. Si Slack répond `invalid_blocks`, renvoyez le message sans les blocs image.

## 4. Fichiers joints

Exemple : [`08-fichiers`](../exemples/08-fichiers/)

L'envoi se fait en trois appels : `files.getUploadURLExternal`, envoi du contenu, puis `files.completeUploadExternal`. L'ancienne méthode `files.upload` est obsolète. Avec `slack_sdk`, `client.files_upload_v2(...)` fait les trois. Un fichier envoyé peut ensuite être affiché dans un bloc `image` avec `{"type": "image", "slack_file": {"id": "<file_id>"}}`, après quelques secondes de traitement.

| Fichier | Librairie | Usage |
|---|---|---|
| Log (`.log`, `.txt`) | aucune | Joint en cas d'échec |
| Export (`.csv`) | `csv`, `pandas`, `polars` | Liste des éléments traités |
| Tableur (`.xlsx`) | `openpyxl`, `xlsxwriter` | Rapport mis en forme |
| Rapport (`.pdf`) | `reportlab`, `weasyprint` | Synthèse hebdomadaire |
| Tableau en image | `dataframe-image`, `great_tables` | Tableau lisible sur mobile |
| Capture d'écran | `playwright`, `selenium` | État d'un site ou d'un tableau de bord |

## 5. Messages dynamiques

Exemples : [`05-suivi-execution`](../exemples/05-suivi-execution/), [`10-messages-programmes`](../exemples/10-messages-programmes/)

| Possibilité | Méthode | Usage |
|---|---|---|
| Modifier un message déjà envoyé | `chat.update` avec le `ts` du message | Progression en direct |
| Répondre dans un fil | `chat.postMessage` avec `thread_ts` | Détail des étapes sous le message principal |
| Répondre dans un fil et dans le canal | idem, avec `"reply_broadcast": true` | Bilan d'échec visible par tous |
| Programmer un message | `chat.scheduleMessage` avec `post_at` | Rappel, message à heure fixe |
| Supprimer un message du bot | `chat.delete` | Message temporaire |
| Message visible par une seule personne | `chat.postEphemeral` avec `user` | Non testé. La personne doit être membre du canal |

## 6. Librairies

| Besoin | Python | JavaScript / Node.js |
|---|---|---|
| Appeler l'API Slack | `requests`, `httpx` | `fetch`, `axios` |
| Client Slack officiel (erreurs, quotas, fichiers) | [`slack_sdk`](https://tools.slack.dev/python-slack-sdk/) | [`@slack/web-api`](https://tools.slack.dev/node-slack-sdk/web-api) |
| Lire le fichier `.env` | `python-dotenv` | `dotenv`, ou `node --env-file=.env` (Node 20+) |
| Application interactive (boutons, commandes, formulaires) | `slack_bolt` | `@slack/bolt` |
| Graphiques | `matplotlib`, `plotly` + `kaleido`, `seaborn` | `chartjs-node-canvas`, `quickchart-js` |
| Captures d'écran | `playwright`, `selenium` | `playwright`, `puppeteer` |
| Envoyer les erreurs du logging vers Slack | `logging.Handler` personnalisé (niveau `ERROR`), ou un sink `loguru` | transport `winston` ou `pino` |

Avec `slack_sdk`, la relance automatique en cas de quota dépassé s'active ainsi :

```python
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler
client.retry_handlers.append(RateLimitErrorRetryHandler(max_retry_count=2))
```

## 7. Fonctions qui demandent des droits supplémentaires

Sans le droit nécessaire, Slack renvoie `missing_scope`.

| Fonction | Droit |
|---|---|
| Ajouter une réaction emoji à un message | `reactions:write` |
| Retrouver une personne à partir de son e-mail | `users:read` + `users:read.email` |
| Écrire dans un canal public sans y inviter le bot | `chat:write.public` |
| Personnaliser le nom et l'icône du bot par message | `chat:write.customize` |
| Lire les informations ou l'historique d'un canal | `channels:read`, `channels:history` (canaux privés : `groups:…`) |
| Épingler un message, ajouter un favori au canal | `pins:write`, `bookmarks:write` |
| Créer ou mettre à jour un canvas | `canvases:write` |
| Boutons d'action, formulaires, commandes slash | interactivité et `commands`, plus un serveur qui reçoit les événements (`slack_bolt`) |

Pour ajouter un droit, sur [api.slack.com/apps](https://api.slack.com/apps) :

1. **OAuth & Permissions**, **Bot Token Scopes**, **Add an OAuth Scope** ;
2. **Reinstall to Workspace**.

Le jeton reste généralement le même après réinstallation. Vérifiez-le avec le [test de l'installation](installation.md#4-tester-lenvoi).
