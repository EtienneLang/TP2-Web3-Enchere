"""
Blueprint pour le Ajax
"""
from flask import Blueprint, render_template, request, redirect, session, current_app as app, jsonify, abort
import bd

bp_api = Blueprint('api', __name__)


@bp_api.route("/recherche")
def chercher_encheres():
    mot_cle = request.args.get("mot-cle")
    indice = request.args.get("indice", type=int, default=0)
    if session and session["utilisateur"]:
        if session["utilisateur"]["est_admin"]:
            est_admin = True
        else:
            est_admin = False
    else:
        est_admin = False
    if not mot_cle or mot_cle == "":
        with bd.creer_connexion() as conn:
            app.logger.info("L'utilisateur va chercher des enchères sur l'accueil sans mot clé")
            encheres = bd.get_encheres(conn, indice, est_admin)
            return jsonify(encheres)
    with bd.creer_connexion() as conn:
        app.logger.info("L'utilisateur va chercher des enchères sur l'accueil avec mot clé")
        encheres = bd.chercher_encheres(conn, mot_cle, indice, est_admin)
        return jsonify(encheres)


@bp_api.route("/miser/<int:id_enchere>", methods=["POST"])
def miser(id_enchere):
    if not session or not session["utilisateur"]:
        app.logger.warning("Un utilisateur non indentifié éssaie de miser sur une enchère")
        abort(401)
    app.logger.info("Un utilisateur éssaie de miser")
    with bd.creer_connexion() as conn:
        enchere = bd.get_enchere(conn, id_enchere)
        mise_max = bd.get_mise_max(conn, id_enchere)
        if not enchere or enchere["est_supprimee"]:
            app.logger.warning("Un utilisateur éssaie de misé sur une enchère non existante ou supprimé")
            abort(404)
        if not enchere["est_active"] or enchere["fk_vendeur"] == session["utilisateur"]["id_utilisateur"]:
            app.logger.warning("Un utilisateur éssaie de misé sur une enchère inactive ou une de ses enchère")
            abort(403)
    mise_montant = request.form.get("txt_mise", type=int)
    if not mise_montant or mise_montant <= 0:
        abort(400)
    if mise_max:
        if mise_montant < mise_max["montant"]:
            abort(400)
    with bd.creer_connexion() as conn:
        if bd.voir_si_deja_mise(conn, session["utilisateur"]["id_utilisateur"], id_enchere):
            bd.modifier_mise(conn, session["utilisateur"]["id_utilisateur"], id_enchere, mise_montant)
            app.logger.info("Modification d'une mise déjà fait sur par un utilisateur")
        else:
            bd.ajouter_mise(conn, session["utilisateur"]["id_utilisateur"], id_enchere, mise_montant)
            app.logger.info("Ajout d'une mise sur l'enchère")
        return bd.get_mise_max(conn, id_enchere)


@bp_api.route("/<int:id_enchere>/misemax")
def get_mise_max(id_enchere):
    with bd.creer_connexion() as conn:
        enchere = bd.get_enchere(conn, id_enchere)
        if not enchere:
            app.logger.warning("Un utilisateur éssaie d'avoir la mise max d'une enchère inexistante")
            abort(404)
        mise_max = bd.get_mise_max(conn, id_enchere)
        app.logger.info("L'API renvois la mise max d'une enchère")
        return jsonify(mise_max)
