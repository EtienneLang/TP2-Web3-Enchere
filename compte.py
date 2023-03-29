from flask import Blueprint, render_template, request, redirect, abort
from app import session
import hashlib
import bd

bp_compte = Blueprint('compte', __name__)
bp_compte.secret_key = "464b2822f3de9cee02fa8a451e18c46ff3db4a0893253c0a54a527c8aa24be93"

@bp_compte.route("/authentifier", methods=["POST","GET"])
def authentifier():

    return render_template("authentifier.jinja")


@bp_compte.route("/deconnecter")
def deconnecter():
    session["utilisateur"].clear()
    return redirect("/")