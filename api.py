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
    if session and session["utilisateur"]:
        if session["utilisateur"]["est_admin"]:
            est_admin = True
        else:
            est_admin = False
    else:
        est_admin = False
    if not mot_cle:
        with bd.creer_connexion() as conn:
            encheres = bd.get_encheres(conn, indice, est_admin)
        return jsonify(encheres)
