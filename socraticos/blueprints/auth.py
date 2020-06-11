from flask import Blueprint, request, abort, session, jsonify, render_template
from firebase_admin.auth import verify_id_token
from socraticos import fireClient
import uuid

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["POST"])
def login():
    content = request.json
    if not content or not content["token"]:
        abort(400, "Request must include JSON body with Firebase ID token")
    
    token = content["token"]
    try:
        result = verify_id_token(token)
        uid = result["uid"]
        user = fireClient.collection("users").document(uid).get()
        if not user.exists:
            abort(400, "User does not exist")
        session["userID"] = uid
        return jsonify(success=True)
    except:
        abort(400, "Invalid token")

@auth.route("/logout", methods=["POST"])
def logout():
    session.pop("userID", None)
    return jsonify(success=True)