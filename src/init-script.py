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
def instalar_ufw():
    try:
        subprocess.run(["sudo", "apt-get", "install", "ufw", "-y"])
        print("UFW instalado correctamente.")
    except Exception as e:
        print(f"Error al instalar UFW: {e}")


# INSTALAR TCPDUMP
def instalar_tcpdump():
    try:
        subprocess.run(["sudo", "apt-get", "install", "tcpdump", "-y"])
        print("tcpdump instalado correctamente.")
    except Exception as e:
        print(f"Error al instalar UFW: {e}")


def configurar_reglas_basicas():
    try:
        reglas = [
            "allow out 80 comment 'Permitido dns'",
            "allow out 443 comment 'Permitido https'",
            "allow out 53 comment 'Permitido dns'",
            "allow 4845 comment 'Permitido puerto del firewall'",
            "allow out 8085 comment 'Permitido sistema sigcenter'",
            "allow out 8092 comment 'Permitido facturacion'",
            "allow 'Nginx Full' comment 'Permitido sistema por nginx'",
            "allow out to 192.168.0.115 port 3306 comment 'Permitido acceso a base de datos'",
            "allow from 186.101.189.104 to any port 3030 comment 'Permitido acceso mediante ssh a la ip 186.101.189.104'",
            "allow from 45.164.64.138 to any port 3030 comment 'Permitido acceso mediante ssh a la ip 45.164.64.138'",
            "allow from 157.100.89.95 to any port 3030 comment 'Permitido acceso mediante ssh a la ip 157.100.89.95'",
        ]

        for regla in reglas:
            subprocess.run(shlex.split(f"/sbin/ufw {regla}"))

        # Bloquear todo con iptables
        subprocess.run(["/sbin/iptables", "-P", "INPUT", "DROP"])
        subprocess.run(["/sbin/iptables", "-P", "OUTPUT", "DROP"])

        # Bloquear todo con UFW
        subprocess.run(["/sbin/ufw", "default", "deny", "incoming"])
        subprocess.run(["/sbin/ufw", "default", "deny", "outgoing"])

        # Habilitar ufw
        subprocess.run(["/sbin/ufw", "enable"])

        print("Reglas básicas de UFW configuradas correctamente.")

        return reglas
    except Exception as e:
        print(f"Error al configurar reglas básicas de UFW: {e}")


def guardar_reglas_basicas():
    reglas = configurar_reglas_basicas()

    # Crear tablas
    createTable.createTables()
    fecha_creacion = datetime.now()
    rule_type = "predefinida"

    firewall = Firewall(
        0,
        "Reglas Predeterminadas",
        rule_type,
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
    instalar_ufw()
    instalar_tcpdump()

    # Crear tablas y guardar datos
    guardar_reglas_basicas()
