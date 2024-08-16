from flask import Flask, render_template
from flask_socketio import SocketIO
import time
import threading

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

# Archivo de log para bloqueos realizados
BLOCK_LOG_FILE = "/var/log/bloqueos_ip.log"


# Ruta básica para servir la página principal
@app.route("/")
def index():
    return render_template("index.html")


# Función para monitorear el archivo de bloqueos
def monitor_block_log():
    last_position = 0
    while True:
        with open(BLOCK_LOG_FILE, "r") as f:
            f.seek(last_position)
            new_lines = f.readlines()
            last_position = f.tell()
            for line in new_lines:
                # Emitir cada nueva línea a través de SocketIO
                socketio.emit("block_notification", {"message": line.strip()})
        # Esperar un tiempo antes de volver a leer el archivo
        time.sleep(1)


# Iniciar el monitoreo del archivo en un hilo separado
threading.Thread(target=monitor_block_log, daemon=True).start()

if __name__ == "__main__":
    socketio.run(app, debug=True)
