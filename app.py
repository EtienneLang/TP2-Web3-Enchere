"""
Démonstration des paramètres obligatoires
"""

from flask import Flask, redirect, render_template, request, abort, session
import bd

from compte import bp_compte
from encheres import bp_encheres
app = Flask(__name__)

app.register_blueprint(bp_compte, url_prefix="/compte")
app.register_blueprint(bp_encheres, url_prefix="/encheres")
app.secret_key = "464b2822f3de9cee02fa8a451e18c46ff3db4a0893253c0a54a527c8aa24be93"


@app.route('/')
def index():
    """Affiche l'accueil"""
    with bd.creer_connexion() as conn:
        encheres = bd.get_encheres(conn)
    return render_template('index.jinja', encheres=encheres)

