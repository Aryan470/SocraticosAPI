from firebase_admin import credentials, firestore
from flask_cors import CORS
from flask import make_response
import firebase_admin
import json, os
from jose import jws


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
    CORS(app, cors_allowed_origins="*")
    app.register_blueprint(users.users, url_prefix="/users")
    app.register_blueprint(groups.groups, url_prefix="/groups")
    app.register_blueprint(auth.auth, url_prefix="/auth")

    @app.before_request
    def log_request_info():
        json_body = request.get_json()
        app.logger.debug('JSON: %s', json_body)
        if json_body:
            if "session" in json_body:
                print("Session string:", json_body["session"])
                session_dict = json.loads(jws.verify(json_body["session"], app.secret_key, algorithms=["HS256"]))
                for key in session_dict:
                    session[key] = session_dict[key]


    @app.after_request
    def encodeSession(response):
        if response.status == 200:
            body_data = response.get_json()
            session_data = {}
            for key in session:
                session_data[key] = session[key]
            encoded_str = jws.sign(session_data, app.secret_key, algorithm='HS256')
            print("Session string:", encoded_str)
            return make_response({"content": body_data, "session": encoded_str})
        else:
            return make_response(response)

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
