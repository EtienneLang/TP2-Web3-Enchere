from flask import Blueprint, render_template, request, redirect, abort, session
import hashlib
import bd

bp_compte = Blueprint('compte', __name__)


@bp_compte.route("/authentifier", methods=["GET", "Post"])
def authentifier():
    """Permets d'autentifier un utilisateur"""
    if request.method == "POST":
        courriel = request.form.get("courriel", default="")
        if len(courriel) == 0:
            return render_template("authentifier.jinja", classe_courriel="is-invalid",
                                   texte_invalide="Veuillez entrez votre adresse email")
        mdp = request.form.get("mdp")
        if not mdp:
            return render_template("authentifier.jinja", classe_mdp="is-invalid",
                                   texte_invalide="Veuillez entrer un mot de passe", courriel=courriel)
        mdp = hacher_mdp(mdp)
        with bd.creer_connexion() as conn:
            utilisateur = bd.authentifier(conn, courriel, mdp)
            if not utilisateur:
                return render_template("authentifier.jinja", courriel=courriel, classe_mdp="is-invalid",
                                       texte_invalide="Le mot de passe ou l'adresse courriel est invalide")
            else:
                session.permanent = True
                session["utilisateur"] = utilisateur
                return redirect("/", code=303)
    else:
        return render_template("authentifier.jinja")


@bp_compte.route("/creer", methods=["Get", "Post"])
def creer_compte():
    """Permets de créer un compte"""
    if request.method == "GET":
        return render_template("creer.jinja")

    nom = request.form.get("nom", default="")
    courriel = request.form.get("courriel", default="")
    mdp = request.form.get("mdp")
    mdp2 = request.form.get("mdp2")
    if not mdp == mdp2:
        return render_template("creer.jinja", nom=nom, courriel=courriel, classe_mdp="is-invalid")
    mdp = hacher_mdp(mdp)
    utilisateur = {
        "courriel": courriel,
        "nom": nom,
        "mdp": mdp
    }
    with bd.creer_connexion() as conn:
        utilisateur["id"] = bd.creer_compte(conn, utilisateur)
    session["utilisateur"] = utilisateur
    return redirect("/", code=303)


@bp_compte.route("/deconnecter")
def deconnecter():
    session["utilisateur"].clear()
    return redirect("/")


def hacher_mdp(mdp_en_clair):
    """Prend un mot de passe en clair et lui applique une fonction de hachage"""
    return hashlib.sha512(mdp_en_clair.encode()).hexdigest()