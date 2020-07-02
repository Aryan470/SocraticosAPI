from socraticos import fireClient
import datetime
import uuid
from flask import Blueprint, request, session
from flask_socketio import join_room, leave_room, send, emit, ConnectionRefusedError
from . import users
from .. import socketio
from jose import jws
from os import environ
import json

@socketio.on("join")
def on_join(data):
    data = json.loads(data)
    session_dict = json.loads(jws.verify(data["session"], getSecretKey(), algorithms=["HS256"]))
    for key in session_dict:
        session[key] = session_dict[key]

    if "userID" not in session:
        return ConnectionRefusedError("Must be logged in to join chat")
    user = users.getUser(session["userID"])
    groupID = data["GROUPID"]

    if groupID not in user["enrollments"] and groupID not in user["mentorships"] and not user["admin"]:
        return ConnectionRefusedError("User is not a student or mentor in the requested group")

    session["user"] = user
    session["groupID"] = groupID

    join_room(groupID)
    sendSession()
    send(str("%s has joined the chat." % user["name"]), room=groupID)

@socketio.on("newMessage")
def receiveMessage(data):
    data = json.loads(data)
    messageText = data["text"]
    session_dict = json.loads(jws.verify(data["session"], getSecretKey(), algorithms=["HS256"]))
    for key in session_dict:
        session[key] = session_dict[key]

    user = session["user"]
    groupID = session["groupID"]

    msg_data = logMessage(messageText, user["userID"], groupID)
    emit("newMessage", msg_data, room=groupID)

@socketio.on("leave")
def on_leave(data):
    data = json.loads(data)
    session_dict = json.loads(jws.verify(data["session"], getSecretKey(), algorithms=["HS256"]))
    for key in session_dict:
        session[key] = session_dict[key]

    name = session["user"]["name"]
    groupID = session["groupID"]

    session.pop("user", None)
    session.pop("groupID", None)

    leave_room(groupID)
    sendSession()
    emit("leave")
    send(str("%s has left the chat." % name), room=groupID)

def sendSession():
    # Encode session into string and send to client, called on join/leave
    session_data = {}
    for key in session:
        session_data[key] = session[key]
    emit("session", {"session": jws.sign(session_data, getSecretKey(), algorithm='HS256')})

def getSecretKey():
    return environ.get("SECRET_KEY", "DEVELOPMENT")

def pinMessage(messageID: str, authorID: str, groupID: str, unpin: bool = False):
    group_ref = fireClient.collection("groups").document(groupID)
    group_obj = group_ref.get()
    if not group_obj.exists:
        raise FileNotFoundError("Group does not exist")

    if authorID not in group_obj.get("mentors"):
        raise PermissionError("Must be mentor to pin messages")

    msg_ref = group_ref.collection("chatHistory").document(messageID)
    msg_obj = msg_ref.get()
    if not msg_obj.exists:
        raise FileNotFoundError("Message does not exist")

    source = msg_obj.to_dict()
    source["pinned"] = not unpin
    msg_ref.set(source)
    return source

def logMessage(content: str, authorID: str, groupID: str):
    messageID = str(uuid.uuid4())
    timestamp = str(datetime.datetime.now())
    source = {
        "messageID": messageID,
        "timestamp": timestamp,
        "authorID": authorID,
        "content": content,
        "pinned": False
    }
    groupRef = fireClient.collection("groups").document(groupID)
    if groupRef.get().exists:
        groupRef.collection("chatHistory").document(messageID).set(source)
    else:
        raise FileNotFoundError("Group does not exist")
    return source
