import sys
import os

# Ajouter le chemin du projet
path = '/home/[VOTRE_NOM_UTILISATEUR]/casino_game'
if path not in sys.path:
    sys.path.append(path)

# Importer l'application Flask
from web_server import app as application
