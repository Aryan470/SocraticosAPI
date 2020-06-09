import socraticos
import os

try:
    port = os.environ["PORT"]
except KeyError:
    port = 7000

socraticos.socketio.run(socraticos.create_app(), port=port, debug=True, host="0.0.0.0")