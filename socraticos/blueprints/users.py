from flask import Blueprint, request, abort, jsonify
from socraticos import fireClient
import socraticos.objects
import uuid

users = Blueprint("users", __name__)

@users.route("/<userID>", methods=["GET"])
def getUser(userID):
    doc_ref = fireClient.collection("users").document(userID)
    user = doc_ref.get()
    if user.exists:
        return user.to_dict()
    else:
        abort(404, "User not found")

@users.route("/search", methods=["GET"])
def search():
    query:str = request.args.get("query", default="", type=str)
    maxResults:int = request.args.get("maxResults", default=10, type=int)
    if not query:
        abort(400, "Request must include query (full name)")
    results = fireClient.collection("users").where("name", "==", query).limit(maxResults)
    return jsonify([userDoc.to_dict() for userDoc in results.stream()])

@users.route("/register", methods=["POST"])
def register():
    content = request.json
    uid = str(uuid.uuid4())

    if not content or not content["name"] or not content["email"] or not content["desc"]:
        abort(400, "Request must include JSON body with name, email, and desc")

    source = {
        "name": content["name"],
        "email": content["email"],
        "desc": content["desc"],
        "userID": uid,
        "enrollments": []
    }

    fireClient.collection("users").document(uid).set(source)
    return source