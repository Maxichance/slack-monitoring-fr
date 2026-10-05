# Installation

Comptez environ 15 minutes la première fois, puis 5 minutes pour chaque nouveau projet.

[Retour au README](../README.md)

1. [Le bot Slack et la configuration](#1-le-bot-slack-et-la-configuration)
2. [Récupérer l'ID du canal](#2-récupérer-lid-du-canal)
3. [Ajouter le bot dans le canal](#3-ajouter-le-bot-dans-le-canal)
4. [Tester l'envoi](#4-tester-lenvoi)
5. [Dépannage](#5-dépannage)

## 1. Le bot Slack et la configuration

### 1.1 Créer le bot

À faire une seule fois par espace de travail. Si votre équipe a déjà un bot, passez directement à la section 1.2 et récupérez les valeurs auprès d'elle.

1. Sur [api.slack.com/apps](https://api.slack.com/apps), cliquez sur **Create New App**, puis **From scratch**.
2. Donnez un nom à l'application (par exemple `Vigie`) et choisissez votre espace de travail.
3. Dans **OAuth & Permissions**, section **Bot Token Scopes**, ajoutez :
   - `chat:write` pour envoyer des messages (obligatoire) ;
   - `files:write` et `files:read` pour envoyer des fichiers, des graphiques ou des logs (conseillé).
4. Cliquez sur **Install to Workspace** en haut de la même page, puis validez.
5. Copiez le **Bot User OAuth Token**, qui commence par `xoxb-`.

Selon les réglages de l'espace de travail, l'installation peut nécessiter l'accord d'un administrateur Slack.

### 1.2 Le fichier `.env`

La configuration se trouve dans un fichier `.env` à la racine du projet, jamais dans le code. Copiez `.env.example` en `.env`, puis renseignez :

```dotenv
# Jeton du bot (api.slack.com/apps, OAuth & Permissions, Bot User OAuth Token)
SLACK_BOT_TOKEN=xoxb-...

# URL de base de l'espace de travail, commune à tous les projets
SLACK_WORKSPACE_URL=https://app.slack.com/client/TXXXXXXXXXX

# ID du canal qui reçoit les messages de ce projet (voir section 2)
SLACK_CHANNEL_ID=CXXXXXXXXXX

# false pour couper les envois sans modifier le code
SLACK_ENABLED=true

# Facultatif : ID du membre à mentionner sur les alertes critiques (commence par U)
SLACK_MENTION_ID=
```

- `SLACK_BOT_TOKEN` et `SLACK_WORKSPACE_URL` sont les mêmes pour toute l'équipe.
- `SLACK_CHANNEL_ID` change d'un projet à l'autre.
- Pour trouver `SLACK_WORKSPACE_URL`, ouvrez Slack dans un navigateur : l'URL commence par `https://app.slack.com/client/T…`. Gardez la partie qui va jusqu'à l'identifiant commençant par `T`.

Le fichier `.env` ne doit pas être publié : il doit figurer dans le `.gitignore`. Seul `.env.example`, sans valeurs, est versionné. Toute personne qui possède le jeton peut écrire au nom du bot. En cas de fuite, régénérez-le sur api.slack.com/apps (**OAuth & Permissions**, **Revoke**, puis **Reinstall**).

## 2. Récupérer l'ID du canal

### Depuis l'URL (navigateur)

Ouvrez le canal dans Slack depuis un navigateur. L'URL a cette forme :

```
https://app.slack.com/client/TXXXXXXXXXX/CXXXXXXXXXX
                             └────┬────┘ └────┬────┘
                       espace de travail   ID du canal
                    (SLACK_WORKSPACE_URL)  (SLACK_CHANNEL_ID)
```

L'ID du canal est la dernière partie de l'URL, celle qui commence par `C`.

### Depuis l'application Slack

1. Cliquez sur le nom du canal en haut de l'écran (ou clic droit, **Afficher les détails du canal**).
2. En bas de l'onglet **À propos**, l'ID du canal est affiché avec un bouton pour le copier.

Un ID qui commence par `T` désigne l'espace de travail, un ID qui commence par `U` désigne une personne : ni l'un ni l'autre ne convient ici.

Il est conseillé de créer un canal dédié au projet (par exemple `#vigie-mon-projet`) plutôt que d'utiliser un canal de discussion.

## 3. Ajouter le bot dans le canal

Avec les droits de base, le bot ne peut pas rejoindre un canal de lui-même. Sans invitation, Slack renvoie `not_in_channel`. L'opération est à faire une fois par canal, public ou privé.

### Par une commande

Dans le canal, tapez `/invite @` suivi du nom du bot, sélectionnez-le dans la liste puis validez :

```
/invite @Vigie
```

Slack confirme que le bot a rejoint le canal.

### Par les paramètres du canal

1. Cliquez sur le nom du canal.
2. Ouvrez l'onglet **Intégrations**.
3. Dans **Applications**, cliquez sur **Ajouter une application**.
4. Recherchez le bot et cliquez sur **Ajouter**.

Le même onglet **Intégrations** permet de vérifier que le bot est bien présent.

## 4. Tester l'envoi

Les commandes ci-dessous chargent le `.env` puis envoient un message de test. Elles se lancent depuis la racine du dépôt.

**Python**

```bash
pip install -r exemples/requirements.txt
python exemples/01-premier-message/premier_message.py
```

**Windows (PowerShell)**

```powershell
Get-Content .env | Where-Object { $_ -match '^\s*[^#].*=' } | ForEach-Object {
  $k, $v = $_ -split '=', 2; Set-Item "env:$($k.Trim())" $v.Trim()
}

$body = @{ channel = $env:SLACK_CHANNEL_ID; text = "Test de connexion" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "https://slack.com/api/chat.postMessage" `
  -Headers @{ Authorization = "Bearer $env:SLACK_BOT_TOKEN" } `
  -ContentType "application/json; charset=utf-8" `
  -Body ([System.Text.Encoding]::UTF8.GetBytes($body))
```

**macOS, Linux, Git Bash (curl)**

```bash
set -a; source .env; set +a

curl -s -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"channel\":\"$SLACK_CHANNEL_ID\",\"text\":\"Test de connexion\"}"
```

Le test est réussi si la réponse contient `"ok": true` et que le message apparaît dans le canal. Les mêmes commandes existent en fichiers dans [`exemples/01-premier-message`](../exemples/01-premier-message/).

## 5. Dépannage

Slack répond HTTP 200 même en cas d'erreur : c'est le champ `"ok"` de la réponse qui indique le résultat, et le champ `"error"` qui en donne la cause.

| Erreur | Cause | Solution |
|---|---|---|
| `not_in_channel` | Le bot n'est pas membre du canal | Inviter le bot (section 3) |
| `channel_not_found` | ID de canal incorrect, ou canal privé sans le bot | Vérifier que l'ID commence par `C` (section 2) et inviter le bot |
| `invalid_auth`, `not_authed` | Jeton absent, mal copié, ou `.env` non chargé | Vérifier `SLACK_BOT_TOKEN` et le chargement du `.env` |
| `token_revoked` | Jeton régénéré ou application désinstallée | Récupérer le nouveau jeton sur api.slack.com/apps |
| `missing_scope` | La fonction demande un droit que le bot n'a pas | Ajouter le droit ([possibilités, section 7](possibilites-slack.md#7-fonctions-qui-demandent-des-droits-supplémentaires)) |
| `ratelimited`, HTTP 429 | Plus d'environ un message par seconde | Regrouper les messages ou attendre la durée indiquée par `Retry-After` |
| Aucun message, aucune erreur | Envoi désactivé ou erreur non journalisée | Vérifier `SLACK_ENABLED=true` et les avertissements dans la console |
