from flask import Blueprint, request

users = Blueprint("users", __name__)

@users.route("/<userID>", methods=["GET"])
def getUser(userID):
    return {"userID": userID}

@users.route("/search", methods=["GET"])
def search():
    return {"query": request.args.get("query", "")}

@users.route("/register", methods=["POST"])
def register():
    return {"message": "made new user"}