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


@bp_details.route("/<int:id>/miser", methods=["POST", "GET"])
def miser(id):
    id_mise = id
    if request.method == "POST":
        mise = request.form.get("txt_mise")
        with bd.creer_connexion() as conn:
            mise_minimum = bd.get_enchere(conn, id_mise)

    return redirect("/details/confirmation", code=303)

@bp_details.route("/confirmation")
def confirmation():
    return render_template("confirmation-mise.jinja")