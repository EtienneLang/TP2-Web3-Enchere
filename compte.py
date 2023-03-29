from flask import Blueprint, render_template, request, redirect, abort
from app import session
import hashlib
import bd

bp_compte = Blueprint('compte', __name__)
bp_compte.secret_key = "464b2822f3de9cee02fa8a451e18c46ff3db4a0893253c0a54a527c8aa24be93"

#@bp_compte.route("/authentifier", methods=["POST","GET"])
#def authentifier():
 #   with bd.creer_connexion() as conn:
  #      utilisateurs = bd.get_utilisateurs(conn)
#
 #   if request.method == "POST":
  #      utilisateur_id = request.form.get("id_utilisateur")
   #     with bd.creer_connexion() as conn:
    #        utilisateur = bd.get_utilisateur(conn, utilisateur_id)
     #   session.permanent = True  # Sinon, la session sera supprimée à la fermeture du navigateur (cookie de session)
      #  session['utilisateur'] = utilisateur


    #return render_template("authentifier.jinja", utilisateurs = utilisateurs)


@bp_compte.route("/deconnecter")
def deconnecter():
    session["utilisateur"].clear()
    return redirect("/")