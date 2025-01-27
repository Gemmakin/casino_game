# Démarrer le serveur web
Start-Process python -ArgumentList "web_server.py" -WorkingDirectory "C:\Users\Utilisateur\CascadeProjects\casino_game"

# Attendre un moment
Start-Sleep -Seconds 3

# Démarrer ngrok
Start-Process ".\ngrok.exe" -ArgumentList "http 5000" -WorkingDirectory "C:\Users\Utilisateur\CascadeProjects\casino_game"

# Attendre que ngrok démarre
Start-Sleep -Seconds 10

# Récupérer l'URL publique via curl
$ngrokUrl = (curl http://127.0.0.1:4040/api/tunnels | ConvertFrom-Json).tunnels[0].public_url

Write-Host "URL Publique : $ngrokUrl"

# Mettre à jour le manifest
$manifestPath = "C:\Users\Utilisateur\CascadeProjects\casino_game\manifest.json"
$manifest = Get-Content $manifestPath | ConvertFrom-Json
$manifest.start_url = $ngrokUrl
$manifest | ConvertTo-Json | Set-Content $manifestPath

Write-Host "Manifest mis à jour avec l'URL : $ngrokUrl"
