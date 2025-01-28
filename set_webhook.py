import requests
import json

# Charger la configuration
with open('telegram_config.json', 'r') as config_file:
    config = json.load(config_file)

# URL de l'API Telegram
url = f"https://api.telegram.org/bot{config['bot_token']}/setWebhook"

# Paramètres de la requête
params = {
    'url': config['webhook_url'],
    'drop_pending_updates': True  # Optionnel : supprime les mises à jour en attente
}

# Envoi de la requête
response = requests.get(url, params=params)

# Affichage du résultat
print(response.json())
