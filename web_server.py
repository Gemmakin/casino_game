from flask import Flask, send_from_directory
from flask_cors import CORS
import os
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration des dossiers
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')

@app.route('/')
def home():
    logger.info("Home route accessed")
    return "Casino Royal Bot Web Server is running!"

@app.route('/web/<path:path>')
def serve_web(path):
    logger.info(f"Serving web file: {path}")
    return send_from_directory(STATIC_DIR, path)

@app.route('/manifest.json')
def serve_manifest():
    logger.info("Manifest route accessed")
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'manifest.json')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
