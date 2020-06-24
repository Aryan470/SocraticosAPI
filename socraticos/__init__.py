from firebase_admin import credentials, firestore
from flask_cors import CORS
import firebase_admin
import json, os


cred = credentials.Certificate(json.loads(os.environ["PROJECT_AUTH"]))
firebase_admin.initialize_app(cred)
fireClient = firestore.client()

from flask import Flask, render_template, session, redirect, request
from flask_socketio import SocketIO

socketio = SocketIO(logger=True, manage_session=True)

from socraticos.blueprints import users, groups, chat, auth


def create_app():
    app = Flask(__name__)

    if "SECRET_KEY" in os.environ:
        app.secret_key = os.environ["SECRET_KEY"]
    else:
        app.secret_key = "DEVELOPMENT"
    CORS(app)
    app.register_blueprint(users.users, url_prefix="/users")
    app.register_blueprint(groups.groups, url_prefix="/groups")
    app.register_blueprint(auth.auth, url_prefix="/auth")

    @app.before_request
    def log_request_info():
        app.logger.debug('JSON: %s', request.get_json())

    # Redirect to API documentation
    @app.route("/")
    def index():
        return redirect("https://documenter.getpostman.com/view/1242833/SzzhcxvZ?version=latest")
        
    ## FIXME: ONLY FOR DEVELOPMENT PURPOSES
    @app.route("/st")
    def st():
        return render_template("st.html")
    
    socketio.init_app(app, cors_allowed_origins="*")
    return app
