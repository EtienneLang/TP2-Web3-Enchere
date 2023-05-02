"""
Toutes les routes pour les détails d'une enchère et de la modification des enchères
"""

from flask import Blueprint, render_template, request, redirect, abort, session, current_app as app
import bd

bp_encheres = Blueprint('encheres', __name__)


@bp_encheres.route("/<int:id_enchere>")
def details(id_enchere):
    """Permets d'afficher les détails d'une enchère"""
    app.logger.info("L'utilisateur va voir les détails d'une enchère")
    with bd.creer_connexion() as conn:
        enchere = bd.get_enchere(conn, id_enchere)
        if not enchere:
            app.logger.info("L'enchère demandé par l'utilisateur n'existe pas")
            abort(404)
        mise = bd.get_mise_max(conn, id_enchere)
        vendeur = bd.get_utilisateur(conn, enchere["fk_vendeur"])
    # Accès à une enchère supprimée sans être un admin
    if enchere["est_supprimee"] and not session["utilisateur"]["est_admin"]:
        app.logger.info("L'enchère demandé par l'utilisateur est supprimée et il n'est pas un admin")
        abort(404)
    if not mise:
        enchere["mise_max"] = 0
    else:
        enchere["mise_max"] = mise["montant"]
        with bd.creer_connexion() as conn:
            miseur = bd.get_utilisateur(conn, mise["fk_miseur"])
            enchere["miseur"] = miseur["nom"]
    app.logger.info("L'enchère demandé par l'utilisateur est renvoyé par le serveur")
    return render_template("details.jinja", enchere=enchere, vendeur=vendeur)


@bp_encheres.route("/<int:id_enchere>/miser", methods=["POST"])
def miser(id_enchere):
    """Permets à un utilisateur de miser sur une enchère"""
    app.logger.info("L'utilisateur éssaie de miser sur une enchère")
    if not session or not session["utilisateur"]:
        app.logger.info("L'utilisateur éssaie de miser sans être authentifier")
        return redirect("/compte/authentifier")
    with bd.creer_connexion() as conn:
        mise_max = bd.get_mise_max(conn, id_enchere)
        enchere = bd.get_enchere(conn, id_enchere)
    if not enchere or enchere["est_supprimee"]:
        app.logger.info("L'enchère sur laquelle on éssaie de miser n'existe pas ou est supprimée")
        abort(404)
    elif not enchere["est_active"] or enchere["fk_vendeur"] == session["utilisateur"]["id_utilisateur"]:
        app.logger.info("L'enchère sur laquelle on éssaie de miser est inactive ou son vendeur éssaie de miser")
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
        app.logger.info("La mise offerte par l'utilisateur n'est pas valide")
        return render_template("details.jinja",
                               classe_mise=classe_mise,
                               enchere=enchere,
                               mise=mise_max,
                               texte_erreur_mise=texte_erreur_mise)
    with bd.creer_connexion() as conn:
        if bd.voir_si_deja_mise(conn, session["utilisateur"]["id_utilisateur"], id_enchere):
            bd.modifier_mise(conn, session["utilisateur"]["id_utilisateur"], id_enchere, mise_montant)
            app.logger.info("Modification d'une mise déjà fait sur par un utilisateur")
        else:
            bd.ajouter_mise(conn, session["utilisateur"]["id_utilisateur"], id_enchere, mise_montant)
            app.logger.info("Ajout d'une mise sur l'enchère")
    app.logger.info("Mise éffectuée par l'utilisateur, retour aux détails de l'enchère")
    return redirect(f"/encheres/{id_enchere}", code=303)


@bp_encheres.route("/<int:id_enchere>/supprimer", methods=["POST"])
def supprimer_enchere(id_enchere):
    """Permets à un administrateur de supprimer une enchère ou d'annuler sa suppression"""
    if not session or not session["utilisateur"]:
        app.logger.info("L'utilisateur éssaie de supprimer une enchère alors qu'il n'est pas connecté")
        abort(401)
    elif not session["utilisateur"]["est_admin"]:
        app.logger.info("L'utilisateur éssaie de supprimer une enchère alors qu'il n'est pas un admin")
        abort(403)
    with bd.creer_connexion() as conn:
        enchere = bd.get_enchere(conn, id_enchere)
    if not enchere:
        app.logger.info("L'utilisateur éssaie de supprimer une enchère qui n'existe pas")
        abort(404)
    if enchere["est_supprimee"]:
        with bd.creer_connexion() as conn:
            bd.activer_enchere(conn, id_enchere)
            app.logger.info("L'utilisateur annule la suppression de l'enchère")
    else:
        with bd.creer_connexion() as conn:
            bd.supprimer_enchere(conn, id_enchere)
            app.logger.info("L'utilisateur supprime l'enchère")
    app.logger.info("L'utilisateur a modifier l'enchère, retour à la page de détails")
    return redirect(f"/encheres/{id_enchere}", 303)
