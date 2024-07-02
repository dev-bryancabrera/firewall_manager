import os
import subprocess
import sys
import time


def find_script(script_name):
    print(f"Buscando el script {script_name}...")
    for root, dirs, files in os.walk("/"):
        if script_name in files:
            script_path = os.path.join(root, script_name)
            print(f"Script encontrado en: {script_path}")
            return script_path
    print(f"Script {script_name} no encontrado.")
    return None


def create_server_vpn(vpn_name, vpn_asociation, vpn_secret_key):
    script_name = "openvpn.sh"
    script_path = find_script(script_name)

    if not script_path:
        print(f"Script {script_name} no encontrado.")
        return

    try:
        print(f"Ejecutando el script: {script_path}")
        subprocess.run(["chmod", "711", script_path], check=True)

        process = subprocess.Popen(
            [
                "bash",
                script_path,
                "setup_server",
                vpn_name,
                vpn_asociation,
                vpn_secret_key,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())
                update_progress(output.strip())
            time.sleep(0.1)

        process.wait()
        if process.returncode != 0:
            print(f"Error ejecutando el comando: {process.returncode}")
            print(f"Error estándar: {process.stderr.read().strip()}")
        else:
            print("Script ejecutado con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando el comando: {e}")
        print(f"Salida estándar: {e.stdout}")
        print(f"Error estándar: {e.stderr}")


def update_progress(message):
    progress_messages = {
        "0%": 0,
        "10%": 10,
        "20%": 20,
        "40%": 40,
        "60%": 60,
        "80%": 80,
        "90%": 90,
        "100%": 100,
    }
    for key, value in progress_messages.items():
        if key in message:
            print(f"Progreso: {value}%")
            sys.stdout.write(
                "\r[" + "#" * (value // 10) + " " * (10 - value // 10) + f"] {value}%"
            )
            sys.stdout.flush()


# Llama a la función con los argumentos necesarios
create_server_vpn("servervpn-sigcenter", "IntelHome CA", "admin-openvpn")
