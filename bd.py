"""
Connexion à la BD
"""
import datetime
import types
import contextlib
import mysql.connector
import hashlib


@contextlib.contextmanager
def creer_connexion():
    """Pour créer une connexion à la BD"""
    conn = mysql.connector.connect(
        user="garneau",
        password="qwerty123",
        host="127.0.0.1",
        database="tp2_enchere",
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


def get_encheres(conn):
    """Retourne toutes les enchères dans la bd"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT * FROM `enchere` ORDER BY date_limite DESC"
        )
        encheres = curseur.fetchall()
        for e in encheres:
            if e['date_limite'] >= datetime.date.today():
                e['est_active'] = True
        return encheres


def get_messages_pour(conn, identifiant):
    """Retourne les messages pour un utilisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT contenu, nom, fk_auteur FROM message " +
            "INNER JOIN utilisateur on fk_auteur=id_utilisateur " +
            "WHERE fk_destinataire=%(id)s",
            {
                "id": identifiant
            }
        )
        return curseur.fetchall()



def ajouter_message(conn, auteur, destinataire, contenu):
    """Pour ajouter un message à un utilisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "INSERT INTO message (contenu, fk_auteur, fk_destinataire) " +
            "VALUES (%(contenu)s, %(fk_auteur)s, %(fk_destinataire)s)",
            {
                "contenu": contenu,
                "fk_auteur": auteur,
                "fk_destinataire": destinataire
            }
        )


def ajouter_amitie(conn, id1, id2):
    """Ajoute un lien d'amitié entre id1 et id2"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "INSERT INTO amitie " +
            "(fk_utilisateur, fk_ami) VALUES (%(id1)s, %(id2)s)",
            {
            "id1": id1,
            "id2": id2
            }
        )
def authentifier(conn, courriel, mdp):
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT * FROM utilisateur WHERE courriel=%(courriel)s AND mdp=%(mdp)s",
            {
                "courriel": courriel,
                "mdp": mdp
            }
        )
        return curseur.fetchone()
