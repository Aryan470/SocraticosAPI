from flask import Blueprint, request

chat = Blueprint("chat", __name__)

@chat.route("/<groupID>", methods=["GET"])
def getChat(groupID):
    return {"websocket": "here is a websocket for chatting in group %s" % groupID}