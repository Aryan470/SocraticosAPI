from flask import Blueprint, request

groups = Blueprint("groups", __name__)

@groups.route("/<groupID>", methods=["GET"])
def getGroup(groupID):
    return {"groupID": groupID}

@groups.route("/search", methods=["GET"])
def search():
    return {"query": request.args.get("query", "")}

@groups.route("/list", methods=["GET"])
def listGroups():
    return {"message": "these are all the groups"}

@groups.route("/chatHistory/<groupID>", methods=["GET"])
def chatHistory(groupID):
    return {"accessing": "chat history", "groupID": groupID}

@groups.route("/pinnedHistory/<groupID>", methods=["GET"])
def pinnedHistory(groupID):
    return {"accessing": "pinned history", "groupID": groupID}

@groups.route("/pin/<groupID>/<messageID>")
def pinMessage(groupID, messageID):
    return {"message": str("pinned message %s in group %s" % (groupID, messageID))}