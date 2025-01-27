from flask import Flask, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Configuration des dossiers
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')

@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(STATIC_DIR, path)

@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'manifest.json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
