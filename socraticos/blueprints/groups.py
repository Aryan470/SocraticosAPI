from flask import Blueprint, request, abort, jsonify
from socraticos import fireClient

groups = Blueprint("groups", __name__)

@groups.route("/<groupID>", methods=["GET"])
def getGroup(groupID):
    doc_ref = fireClient.collection("groups").document(groupID)
    group = doc_ref.get()
    if group.exists:
        return group.to_dict()
    else:
        abort(404, "Group not found")

@groups.route("/search", methods=["GET"])
def search():
    query:str = request.args.get("query", default="", type=str)
    maxResults:int = request.args.get("maxResults", default=10, type=int)
    if not query:
        abort(400, "Request must include query (group name)")
    results = fireClient.collection("groups").where("name", "==", query).limit(maxResults)
    return jsonify([group.to_dict() for group in results.stream()])

@groups.route("/list", methods=["GET"])
def listGroups():
    groups = fireClient.collection("groups").stream()
    return jsonify([group.to_dict() for group in groups])

@groups.route("/chatHistory/<groupID>", methods=["GET"])
def chatHistory(groupID):
    maxResults:int = request.args.get("maxResults", default=10, type=int)
    doc_ref = fireClient.collection("groups").document(groupID)
    group = doc_ref.get()
    if group.exists:
        chatHist = doc_ref.collection("chatHistory").limit(maxResults).stream()
        return jsonify([msg.to_dict() for msg in chatHist])
    else:
        abort(404, "Group not found")

@groups.route("/pinnedHistory/<groupID>", methods=["GET"])
def pinnedHistory(groupID):
    maxResults:int = request.args.get("maxResults", default=10, type=int)
    doc_ref = fireClient.collection("groups").document(groupID)
    if doc_ref.get().exists:
        chatHist = doc_ref.collection("pinnedHistory").limit(maxResults).stream()
        return jsonify([msg.to_dict for msg in chatHist])
    else:
        abort(404, "Group not found")

@groups.route("/pin/<groupID>/<messageID>", methods=["POST"])
def pinMessage(groupID, messageID):
    doc_ref = fireClient.collection("groups").document(groupID)
    if doc_ref.get().exists:
        msg_ref = doc_ref.collection("chatHistory").document(messageID)
        msg = msg_ref.get()
        if msg.exists:
            pinned_msg_ref = doc_ref.collection("pinnedHistory").document(msg.get("messageID"))
            pinned_msg_ref.set(msg.to_dict())
            return msg.to_dict()
        else:
            abort(404, "Message not found")
    else:
        abort(404, "Group not found")
