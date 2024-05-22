from datetime import datetime
import shlex
import subprocess
from models.db.createTables import createTable

# Entidades
from models.entities.firewall import Firewall
from models.entities.firewallDetail import FirewallDetail

# Modelo Entidades
from models.modelFirewall import modelFirewall
from models.modelFirewallDetail import modelFirewallDetail


# INSTALAR UFW
def instalar_paquetes():
    try:
        subprocess.run(["sudo", "apt-get", "install", "ufw", "-y"])
        subprocess.run(["sudo", "apt-get", "install", "dnsutils", "-y"])
        subprocess.run(["sudo", "apt-get", "install", "tcpdump", "-y"])
        subprocess.run(["sudo", "apt-get", "install", "arp-scan", "-y"])
        # subprocess.run(["sudo", "apt-get", "install", "iptables-persistent", "-y"])

        print("Paquetes instalados correctamente.")
    except Exception as e:
        print(f"Error al instalar los paquetes: {e}")


def configurar_reglas_basicas():
    try:
        # Base de datos
        subprocess.run(
            shlex.split(
                "/sbin/ufw allow out to 192.168.100.43 port 3306 comment 'Acceso a base de datos'"
            )
        )

        reglas = [
            "allow 4845 comment 'Puerto del sistema firewall'",
            "allow 8085 comment 'Puerto del sistema SIGCENTER'",
            "allow 8092 comment 'Puerto de entrada para facturacion'",
            "allow out 80 comment 'Puerto de comunicacion HTTP'",
            "allow out 443 comment 'Puerto de comunicacion HTTPS'",
            "allow out 53 comment 'Puerto de comunicacion DNS'",
            "allow out 8092 comment 'Puerto para facturacion'",
            "allow out 8085 comment 'Puerto para recibir respuesta de SIGCENTER'",
            "allow out 18087 comment 'Puerto para uso de API WhatsApp'",
            "allow out 4080 comment 'Puerto para uso de firma electronica'",
            # Conexion ssh
            "allow from 186.101.189.104 to any port 3000 comment 'Acceso mediante ssh a Intelho'",
            "allow from 192.168.100.0/24 to any port 3000 comment 'Acceso mediante ssh local'",
            "allow from 45.164.64.138 to any port 3000 comment 'Acceso mediante ssh a Bryan'",
            "allow from 157.100.89.95 to any port 3000 comment 'Acceso mediante ssh a Michael'",
            # Conexion base de datos
            "allow from 157.100.89.95 to any port 3306 comment 'Acceso a base de datos a Michael'",
            "allow from 186.101.189.104 to any port 3306 comment 'Acceso a base de datos a Intelho'",
            "allow from 45.164.64.138 to any port 3306 comment 'Acceso a base de datos a Bryan'",
        ]

        for regla in reglas:
            subprocess.run(shlex.split(f"/sbin/ufw {regla}"))

        # Bloquear todo con UFW
        subprocess.run(["/sbin/ufw", "default", "deny", "incoming"])
        subprocess.run(["/sbin/ufw", "default", "deny", "outgoing"])

        print("Reglas básicas de UFW configuradas correctamente.")

        return reglas
    except Exception as e:
        print(f"Error al configurar reglas básicas de UFW: {e}")


def guardar_reglas_basicas():
    reglas = configurar_reglas_basicas()

    # Crear tablas
    createTable.createTables()
    fecha_creacion = datetime.now()

    firewall = Firewall(
        0,
        "Reglas Predeterminadas",
        "predefinida",
        fecha_creacion,
        1,
        2,
    )

    firewall = modelFirewall.insertRule(firewall)
    id_rule = firewall.id

    for rule in reglas:
        firewallDetail = FirewallDetail(0, id_rule, rule, 1)
        modelFirewallDetail.insertRuleDetail(firewallDetail)


if __name__ == "__main__":
    # Instalar paquetes necesarios
    instalar_paquetes()

    # Crear tablas y guardar datos
    guardar_reglas_basicas()
