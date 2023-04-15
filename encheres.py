from flask import Blueprint, render_template, request, redirect, abort, session
import hashlib
import bd

bp_encheres = Blueprint('encheres', __name__)


@bp_encheres.route("/<int:id>")
def details(id):
    with bd.creer_connexion() as conn:
        enchere = bd.get_enchere(conn, id)
        if not enchere:
            abort(404)
        mise = bd.get_mise_max(conn, id)
        vendeur = bd.get_utilisateur(conn, enchere["fk_vendeur"])
    # Accès à une enchère supprimée sans être un admin
    if enchere["est_supprimee"] and not session["utilisateur"]["est_admin"]:
        abort(404)
    if not mise:
        enchere["mise_max"] = 0
    else:
        enchere["mise_max"] = mise["montant"]
        with bd.creer_connexion() as conn:
            miseur = bd.get_utilisateur(conn, mise["fk_miseur"])
            enchere["miseur"] = miseur["nom"]

    return render_template("details.jinja", enchere=enchere, vendeur=vendeur)


@bp_encheres.route("/<int:id>/miser", methods=["POST"])
def miser(id):
    if not session["utilisateur"]:
        # Si l'utilisateur n'est pas connecté, on le redirige à l'autentification
        return redirect("/compte/authentifier")
    with bd.creer_connexion() as conn:
        mise_max = bd.get_mise_max(conn, id)
        enchere = bd.get_enchere(conn, id)
    if not enchere or enchere["est_supprimee"]:
        abort(404)
    elif not enchere["est_active"] or enchere["fk_vendeur"] == session["utilisateur"]["id_utilisateur"]:
        abort(400)
    erreur = False
    classe_mise = ""
    mise_montant = request.form.get("txt_mise", type=int)
    if not mise_montant:
        classe_mise = "is-invalid"
        texte_erreur_mise = f"Veuillez entrer une mise"
        erreur = True
    elif mise_montant <= 0:
        classe_mise = "is-invalid"
        texte_erreur_mise = f"La mise dois être plus haute que 0$"
        erreur = True
    elif mise_max:
        if mise_montant <= mise_max["montant"]:
            classe_mise = "is-invalid"
            texte_erreur_mise = f"La mise dois être plus haute que {mise_max['montant']} $"
            erreur = True
    if erreur:
        enchere["mise_max"] = mise_max["montant"]
        return render_template("details.jinja",
                               classe_mise=classe_mise,
                               enchere=enchere,
                               mise=mise_max,
                               texte_erreur_mise=texte_erreur_mise)
    with bd.creer_connexion() as conn:
        bd.ajouter_mise(conn, session["utilisateur"]["id_utilisateur"], id, mise_montant)
    return redirect(f"/encheres/{id}", code=303)


@bp_encheres.route("/<int:id>/supprimer", methods=["POST"])
def supprimer_enchere(id):
    if not session["utilisateur"]:
        abort(401)
    elif not session["utilisateur"]["est_admin"]:
        abort(403)
    with bd.creer_connexion() as conn:
        enchere = bd.get_enchere(conn, id)
    if not enchere:
        abort(404)
    if enchere["est_supprimee"]:
        with bd.creer_connexion() as conn:
            bd.activer_enchere(conn, id)
            return redirect(f"/encheres/{id}", 303)
    else:
        with bd.creer_connexion() as conn:
            bd.supprimer_enchere(conn, id)
            return redirect(f"/encheres/{id}", 303)
