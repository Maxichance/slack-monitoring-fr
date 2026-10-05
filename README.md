# Slack, la vigie de vos projets

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Slack Web API](https://img.shields.io/badge/Slack-Web%20API-4A154B?logo=slack&logoColor=white)](https://api.slack.com/web)
[![Dépendances](https://img.shields.io/badge/d%C3%A9pendances-requests%20%7C%20python--dotenv-informational)](exemples/requirements.txt)
[![Langue](https://img.shields.io/badge/langue-fran%C3%A7ais-blue)](#)

Utiliser un canal Slack pour surveiller ses scripts, pipelines et sites : savoir ce qui tourne, ce qui casse, ce qui change et ce qui est réparé, sans être noyé sous les notifications.

Le dépôt contient un guide d'installation, deux prompts pour faire faire l'intégration par un agent IA, et des exemples Python courts, testés et réutilisables.

```
⏳ Export quotidien · 06:00 (en cours) · ✅✅⏳⬜ 2/4
❌ Export quotidien · 06:00 → 06:03 · ✅✅❌⏭️ · échec : Transformation
🚨 CRITIQUE · Site example.com : le site ne répond pas
✅ Rétabli : Site example.com · retour à la normale après 23 min
ℹ️ Changement détecté : Page tarifs · 1 ligne ajoutée, 1 retirée
```

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Démarrage rapide](#démarrage-rapide)
- [Intégration par un agent IA](#intégration-par-un-agent-ia)
- [Contenu du dépôt](#contenu-du-dépôt)
- [Principes](#principes)
- [Sécurité](#sécurité)

## Fonctionnalités

| | |
|---|---|
| **Suivi d'exécution** | Un message par exécution, mis à jour à chaque étape. Le détail, la trace d'erreur et le log complet arrivent dans le fil. |
| **Alertes** | Cinq niveaux (info, succès, avertissement, erreur, critique), avec couleur, valeurs mesurées et lien. |
| **Surveillance** | Sites et API, seuils, données qui ne se mettent plus à jour. Une alerte quand le problème apparaît, une autre quand il est réglé. |
| **Veille** | Détection des changements d'une page, d'une API ou d'un export, avec les lignes modifiées. |
| **Rapports** | Rapport quotidien avec tableaux, mini-courbes, graphiques et fichiers CSV ou Excel joints. |

## Démarrage rapide

Prérequis : Python 3.9 ou plus récent, et un espace Slack où vous pouvez installer une application.

1. Créez un bot Slack et récupérez son jeton : voir [l'installation, étape 1](docs/installation.md#1-le-bot-slack-et-la-configuration).
2. Copiez `.env.example` en `.env`, puis renseignez le jeton, l'URL de l'espace de travail et l'ID du canal.
3. Invitez le bot dans le canal : `/invite @nom-du-bot`.
4. Lancez le test :

```bash
pip install -r exemples/requirements.txt
python exemples/01-premier-message/premier_message.py
```

Le pas à pas complet, avec le dépannage, est dans [docs/installation.md](docs/installation.md).

## Intégration par un agent IA

[docs/prompt-agent-ia.md](docs/prompt-agent-ia.md) contient deux prompts à coller dans Claude Code, Cursor, Copilot ou ChatGPT :

- **Prompt 1, suivi d'exécution** : l'agent instrumente un projet existant, étape par étape.
- **Prompt 2, vigie** : vous décrivez ce qu'il faut surveiller, l'agent écrit la surveillance, un mode démo et la commande de planification.

## Contenu du dépôt

```
├── README.md
├── .env.example                 modèle de configuration, à copier en .env
├── docs/
│   ├── installation.md          bot, .env, ID du canal, test, dépannage
│   ├── prompt-agent-ia.md       les deux prompts pour agent IA
│   └── possibilites-slack.md    possibilités de Slack, librairies, droits
└── exemples/
    ├── slack.py                 mini-client partagé par tous les exemples
    ├── 01-premier-message/      test de connexion (Python, PowerShell, curl)
    ├── 02-mise-en-forme/        texte, liens, mentions, dates, couleurs
    ├── 03-alertes/              cinq niveaux d'alerte
    ├── 04-vigie/                sites, seuils, changements, fraîcheur des données
    ├── 05-suivi-execution/      suivi d'un script étape par étape
    ├── 06-tableaux/             trois façons d'afficher un tableau
    ├── 07-graphiques/           sparkline, QuickChart, matplotlib
    ├── 08-fichiers/             log, CSV, Excel
    ├── 09-rapport-quotidien/    rapport du matin
    └── 10-messages-programmes/  messages programmés et temporaires
```

Le détail de chaque exemple est dans [exemples/README.md](exemples/README.md).

## Principes

1. **Un message par exécution**, le détail dans le fil : le canal reste lisible.
2. **Une alerte au changement d'état**, jamais en boucle : quand le problème apparaît, puis quand il est réglé.
3. **Les mentions sont réservées au niveau critique.** Pas de `@channel`.
4. **Un rapport quotidien, même quand tout va bien** : s'il n'arrive pas, c'est la surveillance elle-même qui est en panne.

## Sécurité

- Le jeton du bot donne le droit d'écrire au nom du bot dans votre espace Slack. Il se trouve uniquement dans `.env`, exclu par le `.gitignore`.
- Ne l'écrivez pas dans le code et ne le collez pas dans un prompt. En cas de fuite, régénérez-le sur [api.slack.com/apps](https://api.slack.com/apps).
- Pour des données internes ou sensibles, générez les graphiques en local plutôt qu'avec QuickChart : voir [07-graphiques](exemples/07-graphiques/).
