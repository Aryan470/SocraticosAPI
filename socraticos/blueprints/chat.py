from socraticos import fireClient
import datetime
import uuid
from flask import Blueprint, request, session
from flask_socketio import join_room, leave_room, send, emit
from . import users
from .. import socketio

@socketio.on("join")
def on_join(data):
    user = users.getUser(data["USERID"])
    groupID = data["GROUPID"]

    session["user"] = user
    session["groupID"] = groupID

    join_room(groupID)
    send(str("%s has joined the chat :)" % user["name"]), room=groupID)

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

    leave_room(groupID)
    send(str("%s has left the chat :(" % name), room=groupID)

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
