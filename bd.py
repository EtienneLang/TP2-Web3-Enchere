"""
Toutes les requètes à la bd
"""
import datetime
import types
import contextlib
import mysql.connector
import os
from flask import current_app as app
import dotenv


@contextlib.contextmanager
def creer_connexion():
    """Pour créer une connexion à la BD"""
    conn = mysql.connector.connect(
        user=os.getenv("BD_UTILISATEUR"),
        password=os.getenv("BD_MDP"),
        host=os.getenv("BD_SERVEUR"),
        database=os.getenv("BD_NOM_SCHEMA"),
        raise_on_warnings=True
    )

    # Pour ajouter la méthode get_curseur() à l'objet connexion
    conn.get_curseur = types.MethodType(get_curseur, conn)

    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()


@contextlib.contextmanager
def get_curseur(self):
    """Permet d'avoir les enregistrements sous forme de dictionnaires"""
    curseur = self.cursor(dictionary=True)
    try:
        yield curseur
    finally:
        curseur.close()


def get_utilisateurs(conn):
    """Retourne tous les utilisateurs"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT id_utilisateur,courriel,nom FROM utilisateur")
        return curseur.fetchall()


def get_utilisateur(conn, identifiant):
    """Retourne un jeu vidéo"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT * FROM utilisateur WHERE id_utilisateur=%(id_utilisateur)s",
            {
                "id_utilisateur": identifiant
            }
        )
        return curseur.fetchone()


def get_mise_max(conn, identifiant):
    """Permets d'avoir la mise max d'une enchère"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT * FROM mise WHERE fk_enchere = %(id_enchere)s ORDER BY montant DESC LIMIT 1",
            {
                "id_enchere": identifiant
            }
        )
        return curseur.fetchone()


def voir_si_deja_mise(conn, id_miseur, id_enchere,):
    """Permets de vérifier si un utilisateur a déjà misé sur une enchère"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT * FROM mise WHERE fk_enchere = %(id_enchere)s and fk_miseur = %(id_miseur)s",
            {
                "id_enchere": id_enchere,
                "id_miseur": id_miseur
            }
        )
        return curseur.fetchone()


def modifier_mise(conn, id_miseur, id_enchere, montant):
    """Permets de modifier la mise d'un utilisateur sur une enchère"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "UPDATE mise SET montant= %(montant)s WHERE fk_enchere = %(id_enchere)s and fk_miseur = %(id_miseur)s",
            {
                "id_enchere": id_enchere,
                "id_miseur": id_miseur,
                "montant": montant
            }
        )


def ajouter_mise(conn, miseur, enchere, montant):
    """Ajoute une mise dans la table mise"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "INSERT INTO mise(fk_miseur, fk_enchere, montant) VALUES (%(fk_miseur)s, %(fk_enchere)s, %(montant)s)",
            {
                "fk_miseur": miseur,
                "fk_enchere": enchere,
                "montant": montant
            }
        )


def get_encheres(conn):
    """Retourne toutes les enchères dans la bd"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT * FROM `enchere` ORDER BY date_limite DESC"
        )
        encheres = curseur.fetchall()
        for e in encheres:
            verifier_si_enchere_active(e)
        return encheres


def get_enchere(conn, identifiant):
    """Retourne une enchère en fonction de l'id en paramètre"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT * FROM `enchere` WHERE id_enchere = %(id)s",
            {
                "id": identifiant
            }
        )
        enchere = curseur.fetchone()
        verifier_si_enchere_active(enchere)
        return enchere


def get_encheres_utilisateur(conn, id_utilisateur):
    """Retourne toutes les enchères d'un utilisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT * FROM enchere WHERE fk_vendeur = %(id_utilisateur)s ORDER BY date_limite DESC",
            {
                "id_utilisateur": id_utilisateur
            }
        )
        encheres = curseur.fetchall()
        for e in encheres:
            verifier_si_enchere_active(e)
        return encheres


def authentifier(conn, courriel, mdp):
    """Permets d'avoir un utilisateur dans la bd"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT * FROM utilisateur WHERE courriel=%(courriel)s AND mdp=%(mdp)s",
            {
                "courriel": courriel,
                "mdp": mdp
            }
        )
        return curseur.fetchone()


def creer_compte(conn, utilisateur):
    """Permets d'ajouter un compte à la bd"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "INSERT INTO utilisateur (id_utilisateur, courriel, nom, mdp)"
            " VALUES (NULL, %(courriel)s, %(nom)s, %(mdp)s)",
            {
                "courriel": utilisateur["courriel"],
                "nom": utilisateur["nom"],
                "mdp": utilisateur["mdp"]
            }
        )
        return curseur.lastrowid


def verifier_courriel(conn, courriel):
    """Permets de vérifier si un courriel est déjà utilisé dans la bd"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT * FROM utilisateur WHERE courriel=%(courriel)s",
            {
                "courriel": courriel
            }
        )
        return curseur.fetchone()


def get_mises_utilisateur(conn, id_utilisateur):
    """Retourne les mises d'un utilisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT DISTINCT e.*, m.* FROM enchere e INNER JOIN mise m"
            " ON fk_enchere = e.id_enchere WHERE fk_miseur = %(id_utilisateur)s ORDER BY date_limite DESC",
            {
                "id_utilisateur": id_utilisateur
            }
        )
        return curseur.fetchall()


def supprimer_enchere(conn, id_enchere):
    """Permets de supprimer une enchère"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "UPDATE enchere SET est_supprimee = 1 WHERE id_enchere = %(id_enchere)s",
            {
                "id_enchere": id_enchere
            }
        )
    return


def activer_enchere(conn, id_enchere):
    """Permets d'annuler la suppression d'une enchère"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "UPDATE enchere SET est_supprimee = 0 WHERE id_enchere = %(id_enchere)s",
            {
                "id_enchere": id_enchere
            }
        )
    return


def verifier_si_enchere_active(enchere):
    """Permets de vérifier si une enchère est active"""
    if enchere['date_limite'] >= datetime.date.today():
        enchere['est_active'] = True
    else:
        enchere['est_active'] = False
    return enchere
