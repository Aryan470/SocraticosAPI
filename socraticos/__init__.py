from firebase_admin import credentials, firestore
import firebase_admin
import json, os


cred = credentials.Certificate(json.loads(os.environ["PROJECT_AUTH"]))
firebase_admin.initialize_app(cred)
fireClient = firestore.client()

from flask import Flask, render_template
from flask_socketio import SocketIO

socketio = SocketIO(logger=True)

from socraticos.blueprints import users, groups, chat


def create_app():
    app = Flask(__name__)
    app.register_blueprint(users.users, url_prefix="/users")
    app.register_blueprint(groups.groups, url_prefix="/groups")

    ## ONLY FOR DEVELOPMENT PURPOSES
    @app.route("/st")
    def st():
        return render_template("st.html")
    
    socketio.init_app(app, cors_allowed_origins="*")
    return app
