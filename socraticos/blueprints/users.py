from flask import Blueprint, request, abort, jsonify
from socraticos import fireClient
import uuid
from firebase_admin.auth import verify_id_token

users = Blueprint("users", __name__)

@users.route("/<userID>", methods=["GET"])
def getUser(userID):
    doc_ref = fireClient.collection("users").document(userID)
    user = doc_ref.get()
    if user.exists:
        return user.to_dict()
    else:
        abort(404, "User not found")

@users.route("/batch", methods=["GET"])
def getBatch():
    userIDs = request.json["userIDs"]
    userList = [getUser(uid) for uid in userIDs]
    return jsonify(userList)

@users.route("/search", methods=["GET"])
def search():
    query:str = request.args.get("query", default="", type=str).lower()
    maxResults:int = request.args.get("maxResults", default=10, type=int)
    if not query:
        abort(400, "Request must include query (full name)")
    results = fireClient.collection("users").where("tags", "array_contains_any", query.split()).limit(maxResults)
    return jsonify([userDoc.to_dict() for userDoc in results.stream()])

@users.route("/participations/<userID>", methods=["GET"])
def participations(userID):
    user = getUser(userID)
    return jsonify(user["enrollments"] + user["mentorships"])

@users.route("/register", methods=["POST"])
def register():
    content = request.json

    if not content or not content["token"] or not content["name"] or not content["email"] or not content["desc"]:
        abort(400, "Request must include json body with token, name, email, and description")
    token = content["token"]
    try:
        result = verify_id_token(token)
    except:
        abort(400, "Invalid firebase JWT")
    uid = result["uid"]

    user_ref = fireClient.collection("users").document(uid)
    if user_ref.get().exists:
        abort(403, "User already exists")

    taglist = [tag for tag in content["name"].lower().split()]
    source = {
        "name": content["name"],
        "email": content["email"],
        "desc": content["desc"],
        "userID": uid,
        "enrollments": [],
        "mentorships": [],
        "tags": taglist,
        "admin": False
    }

    fireClient.collection("users").document(uid).set(source)
    return source