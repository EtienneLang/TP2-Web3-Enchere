"""
Blueprint pour le Ajax
"""

from flask import Blueprint, render_template, request, redirect, session, current_app as app, jsonify
import bd

bp_api = Blueprint('api', __name__)


@bp_api.route("/recherche")
def chercher_encheres():
    mot_cle = request.args.get("mot_cle")
    indice = request.args.get("indice", type=int, default=0)
    if not mot_cle:
        with bd.creer_connexion() as conn:
            encheres = bd.get_encheres(conn, indice)
        return jsonify(encheres)
