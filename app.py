from socraticos import socketio, create_app
import os

if __name__ == "__main__":
    port = os.environ["PORT"]
    if not port:
        port = 5000
    socketio.run(create_app(), debug=True, port=port)
