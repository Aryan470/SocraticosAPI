from socraticos import fireClient
import datetime
import uuid
from flask import Blueprint, request, session
from flask_socketio import join_room, leave_room, send, emit, ConnectionRefusedError
from . import users
from .. import socketio

@socketio.on("join")
def on_join(data):
    if not session["userID"]:
        return ConnectionRefusedError("Must be logged in to join chat")
    user = users.getUser(session["userID"])
    groupID = data["GROUPID"]

<<<<<<< HEAD
    if groupID not in user["enrollments"] and groupID not in user["mentorships"] and not user["admin"]:
=======
    if groupID not in user["enrollments"] or groupID not in user["mentorships"]:
>>>>>>> e3019a515f5632f8d84421d88951a8b025eae07e
        return ConnectionRefusedError("User is not a student or mentor in the requested group")

    session["user"] = user
    session["groupID"] = groupID

    join_room(groupID)
    send(str("%s has joined the chat." % user["name"]), room=groupID)

@socketio.on("message")
def receiveMessage(messageText):
    user = session["user"]
    groupID = session["groupID"]

    logMessage(messageText, user["userID"], groupID)
    resp = "%s: %s" % (user["name"], messageText)
    send(resp, room=groupID)

@socketio.on("leave")
def on_leave(data):
    name = session["user"]["name"]
    groupID = session["groupID"]

    session.pop("user", None)
    session.pop("groupID", None)

    leave_room(groupID)
    send(str("%s has left the chat." % name), room=groupID)

def logMessage(content: str, authorID: str, groupID: str):
    messageID = str(uuid.uuid4())
    timestamp = str(datetime.datetime.now())
    source = {
        "messageID": messageID,
        "timestamp": timestamp,
        "authorID": authorID,
        "content": content,
    }
    groupRef = fireClient.collection("groups").document(groupID)
    if groupRef.get().exists:
        groupRef.collection("chatHistory").document(messageID).set(source)
    else:
        raise FileNotFoundError("Group does not exist")
