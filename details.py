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
    erreur = False
    classe_mise = ""
    if request.method == "POST":
        mise_montant = request.form.get("txt_mise", type=int)
        with bd.creer_connexion() as conn:
            mise_max = bd.get_mise_max(conn, id_mise)
            enchere = bd.get_enchere(conn, id)
        if mise_montant is None:
            classe_mise = "is-invalid"
            texte_erreur_mise = f"Aucune mise entré"
            erreur = True
        elif not mise_max["max"] and mise_montant <= 0:
            classe_mise = "is-invalid"
            texte_erreur_mise = f"La mise dois être plus haute que 0$"
            erreur = True
        elif mise_max["max"] is not None:
            if mise_montant <= mise_max["max"]:
                classe_mise = "is-invalid"
                texte_erreur_mise = f"La mise dois être plus haute que {mise_max['max']} $"
                erreur = True
        if erreur:
            return render_template("details.jinja", classe_mise=classe_mise, enchere=enchere, mise=mise_max, texte_erreur_mise=texte_erreur_mise)
    return redirect("/details/confirmation", code=303)

@bp_details.route("/confirmation")
def confirmation():
    return render_template("confirmation-mise.jinja")