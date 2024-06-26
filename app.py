"""
TP2 - ENCHÈRES
Route de base
"""

from flask import Flask, render_template
import bd
import dotenv
import os
from compte import bp_compte
from encheres import bp_encheres
from api import bp_api
if not os.getenv("BD_UTILISATEUR"):
    dotenv.load_dotenv('.env')
app = Flask(__name__)
app.register_blueprint(bp_compte, url_prefix="/compte")
app.register_blueprint(bp_encheres, url_prefix="/encheres")
app.register_blueprint(bp_api, url_prefix="/api")
app.secret_key = "464b2822f3de9cee02fa8a451e18c46ff3db4a0893253c0a54a527c8aa24be93"


@app.route('/')
def index():
    """Affiche l'accueil"""
    app.logger.info("L'utilisateur va à l'accueil du site")
    return render_template('index.jinja')
