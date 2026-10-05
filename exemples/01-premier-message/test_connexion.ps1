# Test de connexion sans Python (Windows PowerShell).
# A lancer depuis la racine du depot :  powershell -File exemples/01-premier-message/test_connexion.ps1

# Charger le .env dans la session
Get-Content .env | Where-Object { $_ -match '^\s*[^#].*=' } | ForEach-Object {
  $k, $v = $_ -split '=', 2; Set-Item "env:$($k.Trim())" $v.Trim()
}

$body = @{ channel = $env:SLACK_CHANNEL_ID; text = "Test de connexion depuis PowerShell :white_check_mark:" } | ConvertTo-Json
$reponse = Invoke-RestMethod -Method Post -Uri "https://slack.com/api/chat.postMessage" `
  -Headers @{ Authorization = "Bearer $env:SLACK_BOT_TOKEN" } `
  -ContentType "application/json; charset=utf-8" `
  -Body ([System.Text.Encoding]::UTF8.GetBytes($body))

if ($reponse.ok) { "OK : message envoye" } else { "ERREUR Slack : $($reponse.error)" }
