from socraticos import socketio, create_app
import os

port = os.environ["PORT"]
if not port:
  port = 7000

socketio.run(create_app(), port=port, debug=True)
