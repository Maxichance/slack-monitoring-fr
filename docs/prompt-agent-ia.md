# Prompts pour agent IA

Deux prompts à coller dans un assistant de code (Claude Code, Cursor, GitHub Copilot Chat, Windsurf…) ou dans ChatGPT :

1. [Suivi d'exécution](#prompt-1--suivi-dexécution) : un script ou un pipeline existant envoie un message par étape, les erreurs et un bilan.
2. [Vigie](#prompt-2--vigie) : un script surveille un site, une valeur ou une source de données, et prévient quand l'état change.

Prérequis : avoir suivi l'[installation](installation.md) (bot créé, `.env` renseigné, bot invité dans le canal).

Ne mettez jamais le jeton dans le prompt. Les deux prompts demandent à l'agent de le lire depuis le `.env`.

[Retour au README](../README.md)

## Prompt 1 : suivi d'exécution

Copiez le bloc entier et remplacez les champs entre crochets :

- `[ID_DU_CANAL]` : l'ID du canal ([installation, section 2](installation.md#2-récupérer-lid-du-canal)), par exemple `C0123456789` ;
- `[NOM_DU_PROJET]` : le nom affiché dans les messages, par exemple `Export quotidien` ;
- `[DROITS_DU_BOT]` : les droits accordés au bot ([installation, section 1.1](installation.md#11-créer-le-bot)), par exemple `chat:write, files:write, files:read`.

La ligne « Précisions » en fin de prompt est facultative.

````text
Tu es un développeur senior. Je veux que mon projet m'envoie des logs sur Slack à CHAQUE ÉTAPE de son exécution. Lis entièrement ce message avant d'écrire du code.

## Contexte Slack
- La configuration est dans le fichier .env du projet (n'affiche, ne recopie et ne commite jamais ses valeurs : utilise seulement les noms de variables) :
  - SLACK_BOT_TOKEN : jeton du bot (xoxb-…)
  - SLACK_WORKSPACE_URL : URL de base de l'espace de travail (https://app.slack.com/client/T…)
  - SLACK_CHANNEL_ID : ID du canal cible, ici [ID_DU_CANAL]
  - SLACK_ENABLED : true / false
  - SLACK_MENTION_ID : facultatif, ID du membre à mentionner en cas d'échec (commence par U)
- Nom du projet à afficher dans les messages : [NOM_DU_PROJET]
- Le bot est déjà invité dans le canal cible.
- Droits du bot : [DROITS_DU_BOT]. N'utilise AUCUNE fonction Slack qui demande un autre droit. Avec ces droits, le bot NE PEUT PAS rejoindre un canal seul ni écrire dans un canal dont il n'est pas membre.
- API : POST https://slack.com/api/chat.postMessage
  - en-têtes : "Authorization: Bearer <jeton>" et "Content-Type: application/json; charset=utf-8"
  - corps JSON : {"channel": "<ID canal>", "text": "<texte>", "thread_ts": "<optionnel>"}
  - ATTENTION : Slack répond HTTP 200 même en cas d'erreur. Le vrai résultat est le champ "ok" de la réponse JSON (et "error" s'il vaut false).
  - Limite : environ 1 message par seconde et par canal (sinon erreur HTTP 429 avec un en-tête Retry-After).

## Ce que tu dois faire

### 1. Analyser le projet AVANT de coder
- Détecte le langage, le point d'entrée et la façon dont le projet est lancé (script, CLI, tâche planifiée, API, notebook…).
- Repère les ÉTAPES logiques de l'exécution (par exemple : chargement de la config, extraction, transformation, export, envoi…).
- Donne-moi la liste des étapes que tu as identifiées (fichier et fonction pour chacune) AVANT de modifier le code, puis continue sans attendre ma validation sauf en cas de doute réel.

### 2. Créer un petit module de notification Slack réutilisable
Un seul fichier, par exemple `slack_notifier.py` / `slackNotifier.js` / l'équivalent dans le langage du projet, qui :
- lit SLACK_BOT_TOKEN, SLACK_CHANNEL_ID, SLACK_WORKSPACE_URL et SLACK_ENABLED depuis les variables d'environnement, en chargeant le fichier .env (avec la méthode déjà utilisée par le projet, ou python-dotenv / dotenv sinon) ;
- n'écrit JAMAIS le jeton en dur dans le code, ni dans les logs, ni dans les messages ;
- si le jeton ou l'ID du canal manque, désactive Slack avec un seul avertissement dans les logs locaux, sans faire échouer le programme ;
- si SLACK_CHANNEL_ID contient une URL complète, n'en garde que la dernière partie (l'ID qui commence par C) ;
- appelle l'API directement en HTTP avec la bibliothèque HTTP déjà présente dans le projet (requests, httpx, fetch, axios…). N'ajoute pas de SDK Slack si ce n'est pas nécessaire ;
- utilise un timeout court (10 secondes) ;
- vérifie le champ "ok" de la réponse et, en cas d'échec, écrit un avertissement dans les logs locaux avec le code d'erreur Slack ;
- gère le code 429 en attendant la durée de Retry-After puis en réessayant une fois ;
- NE FAIT JAMAIS PLANTER le programme : toute erreur Slack (réseau, jeton, canal) est attrapée et journalisée localement, puis le programme continue normalement ;
- tronque les textes trop longs (au maximum 3 500 caractères par message).

### 3. Les messages à envoyer (en français, format mrkdwn de Slack)
Règle : UN SEUL message par exécution dans le canal, mis à jour en direct ; tout le détail va dans son fil.
- **Message principal** (envoyé au démarrage, conserve son `ts`) : « ⏳ *[NOM_DU_PROJET]* · run `AAAAMMJJ-HHMMSS` · 06:00 · ⬜⬜⬜⬜ 0/4 ». Modifie-le avec `chat.update` à chaque étape : ⬜ à venir, ⏳ en cours, ✅ réussie, ⚠️ réussie avec avertissement, ❌ en échec, ⏭️ non lancée.
- **Dans le fil** (`thread_ts` = ts du message principal) :
  - au démarrage : la machine (hostname) et le nombre d'étapes prévues ;
  - ✅ `Étape 2/5 · Extraction` · 00:01:23, avec un résumé chiffré si c'est disponible (lignes, fichiers, éléments traités…) ;
  - ⚠️ pour les avertissements importants (données vides, résultat partiel…) ;
  - ❌ `Étape 3/5 · Transformation` échec après 00:00:12, avec le type d'erreur, le message et les 15 dernières lignes de la trace dans un bloc de code.
- **Fin, si tout va bien** : le message principal passe en « ✅ … 06:00 → 06:04 · 4/4 OK · durée », plus un bilan dans le fil. Rien d'autre dans le canal : les succès restent silencieux.
- **Fin, en cas d'échec** : le message principal passe en ❌ avec le nom de l'étape en échec. Le log complet de l'exécution est joint dans le fil (si le droit files:write est disponible). Le bilan est publié dans le fil ET dans le canal (`reply_broadcast: true`), avec un lien cliquable vers le canal (SLACK_WORKSPACE_URL + "/" + SLACK_CHANNEL_ID). Si SLACK_MENTION_ID est renseigné dans le .env, mentionne cette personne avec <@ID>.
- Si le programme s'arrête brutalement (exception non gérée, Ctrl+C), finalise quand même le message principal en ❌ « interrompu » (try/finally, context manager, gestionnaire de sortie ou équivalent).
- Le même identifiant de run apparaît dans le message Slack et dans le nom du fichier de log local.

### 4. Intégration dans le code existant
- Choisis la méthode la moins intrusive : un décorateur, un context manager (`with slack_step("Extraction"):`) ou un wrapper, plutôt que de copier des appels partout.
- Ne change PAS la logique métier, ni l'ordre des étapes, ni le comportement du programme en cas d'erreur (si une étape levait une exception avant, elle doit toujours la lever après l'envoi du message).
- Conserve les logs locaux existants (print, logging…) : Slack vient en plus.

### 5. Livrables attendus
1. Le module de notification.
2. Les modifications dans le code existant (montre-moi les diffs).
3. Un fichier `.env.example` avec les clés SLACK_BOT_TOKEN, SLACK_WORKSPACE_URL, SLACK_CHANNEL_ID et SLACK_ENABLED **sans valeurs**, et la ligne `.env` dans le `.gitignore` si elle n'y est pas.
4. Une commande ou un petit script de test qui envoie « Test de connexion [NOM_DU_PROJET] » et affiche la réponse de Slack.
5. Un résumé court : les fichiers modifiés, les étapes instrumentées et la commande pour tester.

### 6. Si tu n'as pas accès à mes fichiers (par exemple dans ChatGPT)
Ne devine pas la structure de mon projet. Demande-moi d'abord, en une seule question : le langage, le fichier principal et le code (ou la liste) de mes étapes. Ensuite, applique tout ce qui précède à ce que je t'ai donné.

## Si je demande des graphiques, des tableaux ou des fichiers
- Graphique de données internes ou sensibles : génère un PNG en local (matplotlib, plotly + kaleido…) et envoie-le comme fichier avec files.getUploadURLExternal puis files.completeUploadExternal (ou files_upload_v2 avec slack_sdk). Cela demande le droit files:write. N'utilise pas files.upload, qui est obsolète.
- QuickChart.io (URL d'image publique dans un bloc image) seulement pour des données non sensibles, en vérifiant que l'image répond avant l'envoi et en renvoyant le message sans image en cas d'invalid_blocks.
- Tableaux : bloc Block Kit "table" (un seul par message), ou fichier CSV / XLSX joint.

## Erreurs Slack possibles (pour le diagnostic)
- not_in_channel : le bot n'est pas dans le canal ; il faut l'inviter avec "/invite @nom-du-bot" dans le canal.
- channel_not_found : ID de canal faux (il doit commencer par C), ou canal privé où le bot n'a pas été invité.
- invalid_auth / not_authed : jeton manquant ou mal copié dans le .env.
- missing_scope : la fonction utilisée demande un droit que le bot n'a pas.

Précisions sur mon projet (facultatif) : [ex. "script Python lancé chaque nuit par une tâche planifiée", "ne m'envoie que les erreurs", "ajoute le nombre de lignes exportées", "ajoute un graphique de l'évolution sur 30 jours"]
````

Implémentation de référence : [`exemples/05-suivi-execution/suivi_execution.py`](../exemples/05-suivi-execution/suivi_execution.py). Elle peut être jointe au prompt comme modèle.

## Prompt 2 : vigie

Pour surveiller quelque chose plutôt que suivre un script : un site ou une API, une valeur et ses seuils, un contenu qui change (prix, page, export), des données censées être mises à jour chaque jour.

Remplacez les champs entre crochets. La partie « Ce que je veux surveiller » détermine la qualité du résultat : indiquez précisément quoi surveiller et à partir de quand c'est un problème.

````text
Tu es un développeur senior. Je veux une VIGIE : un script qui surveille des choses à intervalle régulier et me prévient sur Slack uniquement quand c'est utile. Lis entièrement ce message avant d'écrire du code.

## Ce que je veux surveiller
[Décris chaque surveillance : QUOI, OÙ, et À PARTIR DE QUAND c'est un problème. Exemples :
 - "Le site https://example.com : critique s'il ne répond pas ou renvoie une erreur 5xx, avertissement s'il met plus de 3 s"
 - "Le nombre de lignes du fichier D:/exports/ventes.csv : avertissement sous 1 000, critique sous 100"
 - "La page https://example.com/tarifs : préviens-moi quand les prix changent, en me montrant ce qui a changé"
 - "Le dossier D:/sauvegardes : erreur si aucun fichier n'a été créé depuis plus de 26 h"]
Fréquence souhaitée : [ex. toutes les 5 minutes / toutes les heures / chaque matin à 8 h]
Où le script tournera : [ex. mon PC Windows, un serveur Linux, GitHub Actions]

## Contexte Slack
- Configuration dans le fichier .env (n'affiche, ne recopie et ne commite jamais ses valeurs) : SLACK_BOT_TOKEN, SLACK_CHANNEL_ID ([ID_DU_CANAL]), SLACK_WORKSPACE_URL, SLACK_ENABLED, et SLACK_MENTION_ID (facultatif : la personne à mentionner sur les alertes critiques).
- Le bot est déjà invité dans le canal. Droits du bot : [DROITS_DU_BOT]. N'utilise aucune fonction qui demande un autre droit.
- API : POST https://slack.com/api/chat.postMessage (en-tête "Authorization: Bearer <jeton>"). Slack répond HTTP 200 même en cas d'erreur : vérifie le champ "ok". Environ 1 message par seconde maximum (HTTP 429 + Retry-After sinon).

## Règles de la vigie (les plus importantes)
1. **Alerter au CHANGEMENT d'état, jamais en boucle.** Mémorise l'état de chaque surveillance dans un petit fichier JSON local (ignoré par git) : statut (ok / avertissement / erreur / critique) et date de début du problème.
   - ok → problème : une alerte.
   - problème → même problème : silence, sauf un rappel toutes les 6 heures si ça dure (« Toujours en cours depuis 6 h »).
   - problème → plus grave : une alerte « Aggravation ».
   - problème → ok : un message « ✅ Rétabli : … après 23 min ».
   - Premier lancement : si tout est ok, aucun message.
2. **Niveaux d'alerte visibles d'un coup d'œil** (barre de couleur via le champ attachments + emoji) : ℹ️ info #1D9BD1, ✅ succès/rétabli #2EB67D, ⚠️ avertissement #ECB22E, ❌ erreur #E01E5A, 🚨 critique #8B0000. **Seul le critique mentionne quelqu'un** (SLACK_MENTION_ID). Jamais de @here ni de @channel.
3. **Chaque alerte se suffit à elle-même** : quoi (en clair), la valeur mesurée et le seuil, depuis quand, et un lien ou un bouton vers la ressource concernée. Le champ "text" (utilisé par les notifications) doit être compréhensible seul.
4. **Détection de changement de contenu** : compare une version NETTOYÉE (texte utile, JSON trié, valeurs extraites) et non le HTML brut. Montre les lignes ajoutées et retirées dans un bloc de code (12 lignes maximum), et joins le diff complet en fichier s'il est plus long.
5. **La vigie ne doit jamais planter** : une surveillance qui échoue (timeout, erreur réseau) est elle-même un statut (erreur ou critique), pas un crash. Une erreur Slack est journalisée localement, puis le script continue.
6. **La vigie doit prouver qu'elle tourne** : propose un rapport quotidien facultatif (un message le matin avec l'état de toutes les surveillances, même si tout est vert).

## Livrables attendus
1. Le script de vigie, avec la liste des surveillances regroupée en haut du fichier, facile à modifier (nom, cible, seuils).
2. Le petit module Slack (envoi, gestion des erreurs, 429) et le module de mémoire d'état.
3. Un mode démo (`--demo`) qui simule une panne, une aggravation, puis un retour à la normale, pour vérifier les messages sans attendre une vraie panne.
4. La commande exacte pour le lancer automatiquement à la fréquence demandée (Planificateur de tâches Windows / cron / GitHub Actions selon l'environnement que j'ai indiqué).
5. `.env.example` sans valeurs, `.env` et le fichier d'état dans le `.gitignore`.
6. Un résumé court : ce qui est surveillé, les seuils, et comment tester.

Si tu n'as pas accès à mes fichiers (par exemple dans ChatGPT), demande-moi d'abord, en une seule question, le langage souhaité et les informations manquantes sur ce que je veux surveiller.
````

Implémentation de référence : [`exemples/04-vigie/`](../exemples/04-vigie/) (site, seuils, changement de contenu, fraîcheur des données).
