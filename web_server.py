from flask import Flask, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Configuration des dossiers
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')

@app.route('/')
def home():
    return "Casino Royal Bot Web Server"

@app.route('/web/<path:path>')
def serve_web(path):
    return send_from_directory(STATIC_DIR, path)

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'manifest.json')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
