from flask import Blueprint, render_template, request, redirect, abort, session
import hashlib
import bd

bp_details = Blueprint('details', __name__)

@bp_details.route("/<int:id>")
def details(id):
    with bd.creer_connexion() as conn:
        enchere = bd.get_enchere(conn, id)
        mise = bd.get_mise_max(conn, id)
        if mise["max"] is None:
            mise["max"] = "Aucune"

        vendeur = bd.get_utilisateur(conn, enchere["fk_vendeur"])

    return render_template("details.jinja", enchere=enchere, mise=mise, vendeur=vendeur)