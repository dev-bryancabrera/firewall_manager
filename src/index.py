from datetime import datetime
import os
import subprocess
import threading
import time
from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from flask_mail import Mail, Message
from config import config
from router.routes import configurar_rutas
from models.entities.notifications import Notification
from models.modelNotification import modelNotification
import configparser

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

csrf = CSRFProtect()
app.config.from_object(config["development"])
login_manager_app = LoginManager(app)
socketio = SocketIO(app)


# Función para cargar configuración de correo electrónico desde un archivo
def load_email_config():
    # Ruta al archivo de configuración
    config_path = os.path.expanduser("~/.email_config")

    # Crear una instancia de ConfigParser
    config = configparser.ConfigParser()

    # Verificar si el archivo existe
    if not os.path.exists(config_path):
        print(
            f"Archivo de configuración de correo electrónico no encontrado: {config_path}"
        )
        # Retornar un diccionario con valores por defecto si el archivo no existe
        return {
            "MAIL_SERVER": "smtp.example.com",
            "MAIL_PORT": 587,
            "MAIL_USE_TLS": True,
            "MAIL_USE_SSL": False,
            "MAIL_USERNAME": "",
            "MAIL_PASSWORD": "",
            "MAIL_DEFAULT_SENDER": "",
        }

    else:
        config.read(config_path)

        email_config = {
            "MAIL_SERVER": config.get("DEFAULT", "MAIL_SERVER"),
            "MAIL_PORT": config.getint("DEFAULT", "MAIL_PORT"),
            "MAIL_USE_TLS": config.getboolean("DEFAULT", "MAIL_USE_TLS"),
            "MAIL_USE_SSL": config.getboolean("DEFAULT", "MAIL_USE_SSL"),
            "MAIL_USERNAME": config.get("DEFAULT", "MAIL_USERNAME"),
            "MAIL_PASSWORD": config.get("DEFAULT", "MAIL_PASSWORD"),
            "MAIL_DEFAULT_SENDER": config.get("DEFAULT", "MAIL_DEFAULT_SENDER"),
        }

        return email_config


# Configuración de Flask-Mail
mail = Mail(app)

configurar_rutas(app, login_manager_app)

file_path = "/home/firewall/iptables/rules.v4"

# Verificar si el archivo existe
if os.path.exists(file_path):
    with open(file_path, "r") as restore:
        subprocess.run(["/sbin/iptables-restore"], stdin=restore)

# Habilitar ufw
# subprocess.run(["/sbin/ufw", "enable"], input="y\n", universal_newlines=True)

subprocess.run(["/sbin/ufw", "reload"], input="y\n", universal_newlines=True)


def status_401(error):
    return redirect(url_for("login"))


def status_404(error):
    return "<h1>Pagina no encontrada</h1>", 404


csrf.init_app(app)
app.register_error_handler(401, status_401)
app.register_error_handler(404, status_404)


def send_email_notification(message, recipient_email):
    """Función para enviar notificación por email."""
    try:
        with app.app_context():  # Establece el contexto de la aplicación
            # Obtener la fecha y hora actual
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M")

            # Renderizar la plantilla HTML con el mensaje y la fecha
            html_body = render_template(
                "email_notification.html",
                nombre="Usuario",
                firma="Firewall",
                mensaje=message,
                fecha=current_time,  # Agrega la fecha y hora actual
            )

            # Crear el mensaje de correo electrónico
            msg = Message(
                subject="Nueva Notificación de Bloqueo",
                sender=app.config["MAIL_DEFAULT_SENDER"],
                recipients=[recipient_email],
                html=html_body,
            )

            # Enviar el correo electrónico
            mail.send(msg)
            print("Correo enviado con éxito!")

    except Exception as e:
        print(f"Error al enviar el correo electrónico: {e}")


def monitor_block_log():
    block_log_file = "/var/log/bloqueos_ip.log"
    last_position_file = "/var/log/last_position.txt"

    # Inicializar la última posición leída
    if os.path.exists(last_position_file):
        with open(last_position_file, "r") as f:
            last_position = int(f.read().strip())
    else:
        last_position = 0
        with open(last_position_file, "w") as f:
            f.write(str(last_position))

    while True:
        with open(block_log_file, "r") as f:
            f.seek(last_position)
            new_lines = f.readlines()
            last_position = f.tell()

        fecha_notificacion = datetime.now()

        for line in new_lines:
            message = line.strip()
            if message:
                # Crear y guardar la notificación en la base de datos
                notification = Notification(0, message, False, fecha_notificacion)
                modelNotification.insertNotification(notification)

                # Emitir la notificación en tiempo real a través de SocketIO
                socketio.emit("block_notification", {"message": message})

                # Reconfigurar y actualizar Mail dentro del contexto de la aplicación
                email_config = load_email_config()
                app.config.update(email_config)
                mail = Mail(app)

                # Enviar un correo electrónico con la notificación
                with app.app_context():  # Establece el contexto de la aplicación
                    send_email_notification(message, app.config["MAIL_DEFAULT_SENDER"])

        with open(last_position_file, "w") as f:
            f.write(str(last_position))

        time.sleep(1)


threading.Thread(target=monitor_block_log, daemon=True).start()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=4845)
