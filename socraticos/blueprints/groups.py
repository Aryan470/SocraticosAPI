from flask import Blueprint, request, abort, jsonify, session
from socraticos import fireClient
from . import chat
import uuid

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
    query:str = request.args.get("query", default="", type=str).lower()
    maxResults:int = request.args.get("maxResults", default=10, type=int)
    if not query:
        abort(400, "Request must include query (group name)")
    results = fireClient.collection("groups").where("tags", "array_contains_any", query.split()).limit(maxResults)
    return jsonify([group.to_dict() for group in results.stream()])

@groups.route("/list", methods=["GET"])
def listGroups():
    groups = fireClient.collection("groups").stream()
    return jsonify([group.to_dict() for group in groups])

@groups.route("/batch", methods=["GET"])
def batchGroups():
    content = request.json
    if not content or not content["groupIDs"]:
        abort(400, "Request must include JSON body of groupID array")
    groupsCollection = fireClient.collection("groups")
    # TODO: use transactions instead
    groupList = [getGroup(groupID) for groupID in content["groupIDs"]]
    return jsonify(groupList)

@groups.route("/create", methods=["POST"])
def createGroup():
    content = request.json
    if not content or not "title" in content or not "description" in content:
        abort(400, "Group needs title and description")
    
    tags = [tag for tag in content["title"].lower().split()]
    groupID = str(uuid.uuid4())
    
    source = {
        "title": content["title"],
        "description": content["description"],
        "students": [],
        "mentors": [], # This should be set to the creator of the group
        "tags": tags,
        "groupID": groupID
    }

    fireClient.collection("groups").document(groupID).set(source)
    return source

@groups.route("/chatHistory/<groupID>", methods=["POST"])
def chatHistory(groupID):
    maxResults:int = request.args.get("maxResults", default=10, type=int)
    doc_ref = fireClient.collection("groups").document(groupID)

    if not "userID" in session:
        abort(401, "Must be logged in to access chat history")
    uid = session["userID"]

    group = doc_ref.get()
    if group.exists:
        group_dict = group.to_dict()
        if uid in group_dict["students"] or uid in group_dict["mentors"]:
            chatHist = doc_ref.collection("chatHistory").order_by("timestamp", direction="DESCENDING").limit(maxResults).stream()
            return jsonify([msg.to_dict() for msg in chatHist])
        else:
            abort(401, "Must be a student or mentor in the group to view chat history")
    else:
        abort(404, "Group not found")

@groups.route("/pinnedHistory/<groupID>", methods=["POST"])
def pinnedHistory(groupID):
    if not "userID" in session:
        abort(401, "Must be logged in to access chat history")
    uid = session["userID"]
    
    maxResults:int = request.args.get("maxResults", default=10, type=int)
    group_ref = fireClient.collection("groups").document(groupID)
    group_info = group_ref.get()
    if group_info.exists:
        group_dict = group_info.to_dict()
        if uid not in group_dict["students"] and uid not in group_dict["mentors"]:
            abort(401, "Must be a student or mentor in the group to view pinned history")
        chatHist = group_ref.collection("chatHistory").where("pinned", "==", True).order_by("timestamp", direction="DESCENDING").limit(maxResults).stream()
        return jsonify([msg.to_dict() for msg in chatHist])
    else:
        abort(404, "Group not found")

@groups.route("/join/<groupID>", methods=["POST"])
def joinGroup(groupID):
    if "userID" not in session:
        abort(403, "Must be logged in to join group")
    
    userID = session["userID"]
    group_ref = fireClient.collection("groups").document(groupID)
    group = group_ref.get()
    if not group.exists:
        abort(404, "Group not found")
    group_info = group.to_dict()

    if userID in group_info["mentors"] or userID in group_info["students"]:
        abort(400, "Cannot join group twice")

    content = request.json
    if not content or not content["role"]:
        abort(400, "Request must include JSON body specifying desired role")
    role = content["role"]

    if role != "student" and role != "mentor":
        abort(400, "Role must either be student or mentor")

    user_ref = fireClient.collection("users").document(userID)
    user = user_ref.get()
    if not user.exists:
        abort(404, "User not found")
    
    user_info = user.to_dict()
    if role == "student":
        user_info["enrollments"].append(groupID)
        group_info["students"].append(userID)
    elif role == "mentor":
        user_info["mentorships"].append(groupID)
        group_info["mentors"].append(userID)
    
    user_ref.set(user_info)
    group_ref.set(group_info)

    return jsonify(success=True)


@groups.route("/setPin/<groupID>/<messageID>", methods=["POST"])
def pinMessage(groupID, messageID):
    if "userID" not in session:
        abort(403, "Must be logged in to pin message")

    content = request.json
    unpin = False
    if content and "unpin" in content:
        unpin = content["unpin"]
    
    try:
        newMessage = chat.pinMessage(messageID, session["userID"], groupID, unpin)
        return newMessage
    except FileNotFoundError:
        abort(404, "Group or message not found")
    except PermissionError:
        abort(403, "Must be logged in as mentor to pin message")
    except:
        abort(400)
