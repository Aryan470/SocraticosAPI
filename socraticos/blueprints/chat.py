from socraticos import fireClient
from socraticos.objects import Message
import datetime
import uuid
from flask import Blueprint, request
from flask_socketio import join_room, leave_room, send

from .. import socketio

@socketio.on("join", namespace="/chat")
def on_join(data):
    name = data["name"]
    group = data["group"]

    join_room(group)
    send(str("%s has joined the chat" % name), room=group)

@socketio.on("leave", namespace="/chat")
def on_leave(data):
    name = data["name"]
    group = data["group"]

    leave_room(group)
    send(str("%s has left the chat" % name), room=group)

def logMessage(content: str, authorID: str, groupID: str):
    messageID = str(uuid.uuid4())
    timestamp = str(datetime.datetime.now())
    msg = Message(messageID, content, authorID, timestamp)
    groupRef = fireClient.collection("groups").document(groupID)
    if groupRef.get().exists:
        groupRef.collection("chatHistory").document(messageID).set(msg.to_dict)
    else:
        raise FileNotFoundError("Group does not exist")
