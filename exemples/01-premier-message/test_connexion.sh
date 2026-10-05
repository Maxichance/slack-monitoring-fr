#!/usr/bin/env bash
# Test de connexion sans Python (Mac / Linux / Git Bash).
# À lancer depuis la racine du dépôt :  bash exemples/01-premier-message/test_connexion.sh

set -a; source .env; set +a   # charger le .env dans la session

curl -s -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"channel\":\"$SLACK_CHANNEL_ID\",\"text\":\"Test de connexion depuis curl :white_check_mark:\"}"
echo
