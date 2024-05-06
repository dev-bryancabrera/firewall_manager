import subprocess
# from src.models.db.createTables import createTable

# Crear tablas
# crearTablas = createTable.createTables()


def instalar_ufw():
    try:
        subprocess.run(["sudo", "apt-get", "install", "ufw", "-y"])
        print("UFW instalado correctamente.")
    except Exception as e:
        print(f"Error al instalar UFW: {e}")


def configurar_reglas_basicas():
    try:
        # Bloquear todo con iptables
        subprocess.run(["sudo", "iptables", "-P", "INPUT", "DROP"])
        subprocess.run(["sudo", "iptables", "-P", "OUTPUT", "DROP"])

        # Habilitar ufw
        subprocess.run(["sudo", "ufw", "enable"])

        # Bloquear todo con UFW
        subprocess.run(["sudo", "ufw", "default", "deny", "incoming"])
        subprocess.run(["sudo", "ufw", "default", "deny", "outgoing"])

        # Permitir el tráfico SSH
        subprocess.run(
            [
                "sudo",
                "ufw",
                "allow",
                "3000",
                "comment",
                "'Permitido comunicacion ssh'",
            ]
        )

        # Permitir el tráfico HTTP
        subprocess.run(
            ["sudo", "ufw", "allow", "out", "80", "comment", "'Permitido http'"]
        )

        # Permitir el tráfico HTTPS
        subprocess.run(
            ["sudo", "ufw", "allow", "out", "443", "comment", "'Permitido https'"]
        )

        # Permitir el tráfico DNS
        subprocess.run(
            ["sudo", "ufw", "allow", "out", "53", "comment", "'Permitido dns'"]
        )

        # Permitir el tráfico Firewall
        subprocess.run(
            [
                "sudo",
                "ufw",
                "allow",
                "4845",
                "comment",
                "'Permitido puerto del firewall'",
            ]
        )

        # Permitir el tráfico al sistema SIGCENTER
        subprocess.run(
            [
                "sudo",
                "ufw",
                "allow",
                "out",
                "8085",
                "comment",
                "'Permitido sistema sigcenter'",
            ]
        )

        # Permitir el tráfico FACTURACION
        subprocess.run(
            [
                "sudo",
                "ufw",
                "allow",
                "out",
                "8212",
                "comment",
                "'Permitido facturacion'",
            ]
        )

        # Permitir el tráfico para ejecutar el sistema con NGINX
        subprocess.run(
            [
                "sudo",
                "ufw",
                "allow",
                "Nginx Full",
                "comment",
                "'Permitido sistema por nginx'",
            ]
        )

        # Permitir el tráfico para la conexion a la base de datos
        subprocess.run(
            [
                "sudo",
                "ufw",
                "allow",
                "out",
                "to",
                "192.168.0.115",
                "port",
                "3306",
                "comment",
                "'Permitido acceso a base de datos'",
            ]
        )

        print("Reglas básicas de UFW configuradas correctamente.")
    except Exception as e:
        print(f"Error al configurar reglas básicas de UFW: {e}")


if __name__ == "__main__":
    # Instalar ufw
    # instalar_ufw()

    # Configurar reglas básicas
    configurar_reglas_basicas()
