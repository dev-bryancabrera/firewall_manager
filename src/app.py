from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import subprocess

# Crear tablas
# from models.db.createTables import createTable

from config import config
from router.routes import configurar_rutas

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
csrf = CSRFProtect()

app.config.from_object(config["development"])
login_manager_app = LoginManager(app)

configurar_rutas(app, login_manager_app)

# Bloquear todo con iptables
block_incoming_command = ["sudo", "iptables", "-P", "INPUT", "DROP"]
block_outgoing_command = ["sudo", "iptables", "-P", "OUTPUT", "DROP"]
subprocess.run(block_incoming_command)
subprocess.run(block_outgoing_command)

# Bloquear todo con UFW
block_all_command = ["sudo", "ufw", "default", "deny", "incoming"]
block_all_command = ["sudo", "ufw", "default", "deny", "outgoing"]
subprocess.run(block_all_command)
subprocess.run(block_all_command)

# crearTablas = createTable.createTables()

def status_401(error):
    return redirect(url_for("login"))


def status_404(error):
    return "<h1>Pagina no encontrada</h1>", 404


csrf.init_app(app)
app.register_error_handler(401, status_401)
app.register_error_handler(404, status_404)

if __name__ == "__main__":
    # csrf.init_app(app)
    # app.config.from_object(config["development"])
    app.run(host="0.0.0.0", port=3000)
