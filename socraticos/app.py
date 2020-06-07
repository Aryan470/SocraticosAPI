from flask import Flask
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import socraticos
from socraticos.blueprints import users, groups, chat

app = Flask(__name__)
app.register_blueprint(users.users, url_prefix="/users")
app.register_blueprint(groups.groups, url_prefix="/groups")
app.register_blueprint(chat.chat, url_prefix="/chat")

@app.route('/test')
def test():
    doc_ref = socraticos.fireClient.collection("users").document("newUUID")
    doc_ref.set({
        "id": "newUUID",
        "fullName": "test user jr.",
        "email": "testuser@example.com",
        "enrollments": ["compsci"]
    })
    return doc_ref.get().to_dict()