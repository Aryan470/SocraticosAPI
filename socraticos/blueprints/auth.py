from os import getenv
from flask import Blueprint, request, abort, session, jsonify, render_template
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer

from firebase_admin.auth import verify_id_token
from socraticos import fireClient
import uuid

auth = Blueprint("auth", __name__)

@auth.route("/testlogin", methods=["POST"])
def test_login():
    content = request.json
    if not content or not content["token"]:
        abort(400, "Request must include JSON body with Firebase ID token")
    
    uid = content["token"]
    user = fireClient.collection("users").document(uid).get()
    if not user.exists:
        abort(400, "User does not exist")
    session["userID"] = uid
    
    token_dict = {"userID": uid}
    return jsonify({"token": encodeFlaskCookie(getSecretKey(), token_dict), "success": True})

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
        token_dict = {"userID": uid}
        return jsonify({"token": encodeFlaskCookie(getSecretKey(), token_dict), "success": True})
    except:
        abort(400, "Invalid token")

@auth.route("/logout", methods=["POST"])
def logout():
    session.pop("userID", None)
    return jsonify(success=True)

def getSecretKey():
    return getenv("SECRET_KEY", "DEVELOPMENT")

class SimpleSecureCookieSessionInterface(SecureCookieSessionInterface):
	# Override method
	# Take secret_key instead of an instance of a Flask app
	def get_signing_serializer(self, secret_key):
		if not secret_key:
			return None
		signer_kwargs = dict(key_derivation=self.key_derivation, digest_method=self.digest_method)
		return URLSafeTimedSerializer(secret_key, salt=self.salt, serializer=self.serializer, signer_kwargs=signer_kwargs)

def encodeFlaskCookie(secret_key, cookieDict):
	sscsi = SimpleSecureCookieSessionInterface()
	signingSerializer = sscsi.get_signing_serializer(secret_key)
	return signingSerializer.dumps(cookieDict)