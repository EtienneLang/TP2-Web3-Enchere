from flask import Blueprint, render_template, request, redirect, session
import hashlib
import bd
import re

bp_compte = Blueprint('compte', __name__)
reg_email = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
reg_html = re.compile(r'<(.*)>.*?|<(.*) />')


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
        return render_template("creer.jinja",
                               invalidation=None
                               )

    invalidation = valider_creation_compte()
    if not invalidation["form_valide"]:
        return render_template("creer.jinja",
                               invalidation=invalidation
                               )
    utilisateur = invalidation
    with bd.creer_connexion() as conn:
        id_utilisateur = bd.creer_compte(conn, utilisateur)
        # pour avoir le champ est_admin
        utilisateur = bd.get_utilisateur(conn, id_utilisateur)
    session["utilisateur"] = utilisateur
    return redirect("/", code=303)


@bp_compte.route("/deconnecter")
def deconnecter():
    """Permets de déconnecter un utilisateur"""
    session["utilisateur"].clear()
    return redirect("/")


@bp_compte.route("/encheres")
def afficher_encheres_utilisateur():
    """Permets d'afficher la page des enchères d'un utilisateur"""
    if not session or not session["utilisateur"]:
        return redirect("/compte/authentifier")
    with bd.creer_connexion() as conn:
        encheres = bd.get_encheres_utilisateur(conn, session['utilisateur']['id_utilisateur'])
        for e in encheres:
            mise_max = bd.get_mise_max(conn, e["id_enchere"])
            if mise_max:
                acheteur = bd.get_utilisateur(conn, mise_max["fk_miseur"])
                e["acheteur"] = acheteur["nom"]
                e["mise_max"] = mise_max["montant"]
            else:
                e["mise_max"] = None
    return render_template("encheres.jinja", encheres=encheres)


@bp_compte.route("/mises")
def afficher_mises_utilisateur():
    if not session["utilisateur"]:
        return redirect("/compte/authentifier")
    with bd.creer_connexion() as conn:
        mises = bd.get_mises_utilisateur(conn, session["utilisateur"]["id_utilisateur"])
    with bd.creer_connexion() as conn:
        for m in mises:
            bd.verifier_si_enchere_active(m)
            mise_max = bd.get_mise_max(conn, m["id_enchere"])
            if mise_max["fk_miseur"] == session["utilisateur"]["id_utilisateur"]:
                m["enchere_leader"] = True
            else:
                m["enchere_leader"] = False
                m["montant_max"] = mise_max["montant"]
    return render_template("mises.jinja", mises=mises)


def hacher_mdp(mdp_en_clair):
    """Prend un mot de passe en clair et lui applique une fonction de hachage"""
    return hashlib.sha512(mdp_en_clair.encode()).hexdigest()


def valider_creation_compte():
    """Permets de valider les champs de la création d'un compte"""
    # récupération des champs et création des classes et textes vide pour la validation
    nom = request.form.get("nom", default="")
    texte_nom = ""
    classe_nom = ""
    courriel = request.form.get("courriel", default="")
    texte_courriel = ""
    classe_courriel = ""
    mdp = request.form.get("mdp")
    texte_mdp = ""
    classe_mdp = ""
    mdp2 = request.form.get("mdp2")
    texte_mdp2 = ""
    classe_mdp2 = ""
    form_valide = True

    # validation du courriel
    if not courriel:
        classe_courriel = "is-invalid"
        texte_courriel = "Veuillez entrer votre adresse courriel"
        form_valide = False
    elif len(courriel) > 50:
        classe_courriel = "is-invalid"
        texte_courriel = "L'adresse courriel ne peut pas contenir plus de 50 caractères"
        form_valide = False
    elif not reg_email.fullmatch(courriel):
        classe_courriel = "is-invalid"
        texte_courriel = "L'adresse courriel ne doit pas contenir de champs interdits et doit être une adresse valide"
        form_valide = False
    else:
        with bd.creer_connexion() as conn:
            email_existant = bd.verifier_courriel(conn, courriel)
            if email_existant:
                classe_courriel = "is-invalid"
                texte_courriel = "L'adresse courriel est déjà utilisée"
                form_valide = False

    # validation du nom
    if not nom:
        classe_nom = "is-invalid"
        texte_nom = "Veuillez entrer votre nom"
        form_valide = False
    elif len(nom) < 3 or len(nom) > 50:
        classe_nom = "is-invalid"
        texte_nom = "Votre nom nom doit contenir entre 3 et 50 caractères"
        form_valide = False
    elif reg_html.fullmatch(nom):
        classe_nom = "is-invalid"
        texte_nom = "Votre nom nom ne peut pas contenir de caractères interdits"
        form_valide = False

    # validation du mot de passe
    mdp_valide = True
    if not mdp:
        classe_mdp = "is-invalid"
        texte_mdp = "Veuillez entrer un mot de passe"
        form_valide = False
        mdp_valide = False
    elif len(mdp) < 4:
        classe_mdp = "is-invalid"
        texte_mdp = "Votre mot de passe doit contenir au moins 4 caractères"
        form_valide = False
        mdp_valide = False
    elif reg_html.fullmatch(mdp):
        classe_mdp = "is-invalid"
        texte_mdp = "Votre mot de passe ne peut pas contenir de caractères interdits"
        form_valide = False
        mdp_valide = False

    # validation des deux mots de passe
    if mdp_valide:
        if not mdp2:
            classe_mdp2 = "is-invalid"
            texte_mdp2 = "Veuillez confirmer votre mot de passe"
            form_valide = False
        elif not mdp == mdp2:
            classe_mdp2 = "is-invalid"
            texte_mdp2 = "Les mots de passe ne concordent pas"
            form_valide = False

    if not form_valide:
        invalidation = {
            "form_valide": form_valide,
            "courriel": courriel,
            "classe_courriel": classe_courriel,
            "texte_courriel": texte_courriel,
            "nom": nom,
            "classe_nom": classe_nom,
            "texte_nom": texte_nom,
            "classe_mdp": classe_mdp,
            "texte_mdp": texte_mdp,
            "classe_mdp2": classe_mdp2,
            "texte_mdp2": texte_mdp2
        }
        return invalidation

    mdp = hacher_mdp(mdp)
    utilisateur = {
        "form_valide": form_valide,
        "courriel": courriel,
        "nom": nom,
        "mdp": mdp
    }
    return utilisateur
