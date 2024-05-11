from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import subprocess


from config import config
from router.routes import configurar_rutas

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
csrf = CSRFProtect()

app.config.from_object(config["development"])
login_manager_app = LoginManager(app)

configurar_rutas(app, login_manager_app)


# Habilitar ufw
with open("/home/firewall/iptables/rules.v4", "r") as restore:
    subprocess.run(["iptables-restore"], stdin=restore)
subprocess.run(["/sbin/ufw", "enable"], input="y\n", universal_newlines=True)


def status_401(error):
    return redirect(url_for("login"))


def status_404(error):
    return "<h1>Pagina no encontrada</h1>", 404


csrf.init_app(app)
app.register_error_handler(401, status_401)
app.register_error_handler(404, status_404)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4845)
