import base64
from datetime import datetime
from io import BytesIO

import shlex
from flask import flash, jsonify
from flask_login import current_user, login_user
import pandas as pd
import paramiko
from scapy.all import *

import re

import subprocess

# Models
from models.modelUser import modelUser
from models.modelFirewall import modelFirewall
from models.modelFirewallDetail import modelFirewallDetail
from models.modelMonitoreo import modelPaquetes
from models.modelFilterPacket import modelFilterPacket

# Entities
from models.entities.user import User
from models.entities.firewall import Firewall
from models.entities.firewallDetail import FirewallDetail
from models.entities.monitoreo import Monitoreo
from models.entities.filterPacket import FilterPacket


# Función para realizar una consulta a la base de datos
def validar_ingreso(username, password_hash):
    try:
        user = User(0, username, password_hash)
        logged_user = modelUser.login(user)
        if logged_user is not None:
            if logged_user.password_hash:
                login_user(logged_user)
                return True
            else:
                flash("Credenciales Erroneas")
                return False
        else:
            flash("Usuario no Encontrado")
            return False
    except Exception as e:
        print("dio un error > ", {str(e)})
        return str(e)


def obtener_reglas_ufw():
    try:
        """ salida = subprocess.check_output(["sudo", "ufw", "status", "numbered"])
        reglas = salida.decode("utf-8").splitlines()

        # Filtrar las líneas que comienzan con '[', eliminar "(out)" y ajustar los espacios en los números
        consulta_formateada = "\n".join(
            [
                re.sub(r"\(out\)", "", re.sub(r"\[\s*(\d+)\]", r"[\1]", line.strip()))
                for line in reglas
                if line.startswith("[")
            ]
        ) """

        reglas_in = []
        reglas_out = []
        reglas_default = []

        rule_db = modelFirewall.getRules()

        if rule_db:
            for rule_tuple in rule_db:
                domain = ""
                domains = ""

                ip = ""
                port = ""
                rule_data = ""

                id_regla = rule_tuple[0]
                assigned_name = rule_tuple[1].replace("_", " ").replace("-", " ")
                status = rule_tuple[4]
                created_date = rule_tuple[3].strftime("%Y-%m-%d")
                tipo_regla = rule_tuple[2]

                detail_domain_rules = modelFirewallDetail.getRulesDetailsById(id_regla)

                for detail_domain in detail_domain_rules:
                    detail_status = detail_domain[2]

                    if tipo_regla == "dominio" or tipo_regla == "contenido":
                        rule_detail_parts = detail_domain[1].split(
                            " -m comment --comment "
                        )
                        rule_detail_command = rule_detail_parts[0].split()

                        if detail_status == 1:
                            count_hyphens = rule_detail_parts[1].count("-")

                            if count_hyphens == 2:
                                domain = (
                                    rule_detail_parts[1]
                                    .split("-", 2)[2]
                                    .strip()
                                    .replace("'", "")
                                )

                            elif count_hyphens == 1:
                                domain = (
                                    rule_detail_parts[1]
                                    .split("-", 1)[1]
                                    .strip()
                                    .replace("'", "")
                                )

                    else:
                        rule_detail_parts = detail_domain[1].split(" comment ")
                        rule_detail_command = rule_detail_parts[0].split()
                        for part in rule_detail_command:
                            if is_valid_ip(part):
                                ip = part

                            elif "port" in part.lower():
                                next_index = rule_detail_command.index(part) + 1
                                next_part = rule_detail_command[next_index]
                                port = next_part
                            elif part.isdigit():
                                port = part

                        if ip and port:
                            rule_data = f"{ip}:{port}"
                        elif ip:
                            rule_data = f"{ip}"
                        elif port:
                            rule_data = f"{port}"

                    if domains:
                        domains += " | " + domain
                    else:
                        domains += domain

                    if (
                        "allow" in rule_detail_command
                        or "ACCEPT" in rule_detail_command
                    ):
                        permiso = "PERMITIDO"
                    elif (
                        "reject" in rule_detail_command
                        or "REJECT" in rule_detail_command
                    ):
                        permiso = "DENEGADO"

                    if "tcp" in rule_detail_command:
                        protocolo = "TCP"
                    elif "udp" in rule_detail_command:
                        protocolo = "UDP"
                    else:
                        protocolo = "TCP/UDP"

                    if "in" in rule_detail_command or "INPUT" in rule_detail_command:
                        entry = "ENTRADA"
                    elif (
                        "out" in rule_detail_command or "OUTPUT" in rule_detail_command
                    ):
                        entry = "SALIDA"
                    else:
                        entry = "ENTRADA"

                    if tipo_regla == "predefinida":
                        regla = {
                            "nombre": assigned_name,
                            "tipo_regla": tipo_regla.title(),
                            "rule_data": rule_data,
                            "accion": permiso,
                            "protocolo": protocolo,
                            "entrada": entry,
                        }

                        reglas_default.append(regla)

                if tipo_regla != "predefinida":
                    regla = {
                        "id_regla": id_regla,
                        "nombre": assigned_name,
                        "fecha_creacion": created_date,
                        "tipo_regla": tipo_regla.title(),
                        "dominio": domains if not rule_data else rule_data,
                        "accion": permiso,
                        "protocolo": protocolo,
                        "entrada": entry,
                        "estado": status,
                    }

                    if entry == "ENTRADA":
                        reglas_in.append(regla)
                    elif entry == "SALIDA":
                        reglas_out.append(regla)

        return reglas_in, reglas_out, reglas_default
    except subprocess.CalledProcessError as e:
        return [{"error": f"Error al obtener reglas UFW: {e}"}]


def is_valid_ip(ip):
    # Expresión regular para verificar el formato de la dirección IP
    ip_regex = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"

    return re.match(ip_regex, ip) is not None


def obtener_reglas_ufw_contenido():
    try:
        reglas_contenido = {}
        reglas_contenido_sorted = {}
        rule_db = modelFirewall.getRulesContent()

        if rule_db:
            for rule_tuple in rule_db:
                id_regla = rule_tuple[0]
                name_rule = rule_tuple[1]

                assigned_name = (
                    name_rule.split(" - ")[1].strip().replace("_", " ").lower().title()
                )

                created_date = rule_tuple[3].strftime("%Y-%m-%d")

                detail_rules = modelFirewallDetail.getRulesDetailsById(id_regla)

                for detail_rule in detail_rules:
                    rule_datail_id = detail_rule[0]
                    rule_string = detail_rule[1]
                    rule_status = detail_rule[2]

                    rule_parts = rule_string.split(" -m comment --comment ")

                    rule_command = rule_parts[0].split()
                    domain = rule_parts[1].split("-", 2)[2].strip().replace("'", "")

                    if "ACCEPT" in rule_command:
                        permiso = "PERMITIDO"
                    elif "REJECT" in rule_command:
                        permiso = "DENEGADO"

                    if "tcp" in rule_command:
                        protocolo = "TCP"
                    elif "udp" in rule_command:
                        protocolo = "UDP"
                    else:
                        protocolo = "TCP/UDP"

                    if "INPUT" in rule_command:
                        entry = "ENTRADA"
                    elif "OUTPUT" in rule_command:
                        entry = "SALIDA"
                    else:
                        entry = "ENTRADA"

                    # Crear un diccionario con los valores
                    regla = {
                        "id_rule": id_regla,
                        "nombre_regla_contenido": name_rule,
                        "id_rule_detail": rule_datail_id,
                        "nombre": domain,
                        "fecha_creacion": created_date,
                        "accion": permiso,
                        "protocolo": protocolo,
                        "entrada": entry,
                        "estado": rule_status,
                    }

                    # Agregar el diccionario al contenido correspondiente en el diccionario reglas_contenido
                    if (assigned_name, id_regla, name_rule) not in reglas_contenido:
                        reglas_contenido[(assigned_name, id_regla, name_rule)] = [regla]
                    else:
                        reglas_contenido[(assigned_name, id_regla, name_rule)].append(
                            regla
                        )
            reglas_contenido_sorted = {}
            for key, value in reglas_contenido.items():
                sorted_value = sorted(value, key=lambda x: x["nombre"])
                reglas_contenido_sorted[key] = sorted_value

        return reglas_contenido_sorted
    except subprocess.CalledProcessError as e:
        return {"error": f"Error al obtener reglas UFW: {e}"}


def scan_network():
    try:
        # Comando arp-scan para escanear la red
        command = "sudo arp-scan -l"
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate()

        # Decodificar la salida del comando arp-scan de bytes a texto
        output = stdout.decode()

        devices = []

        pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

        for line in output.split("\n"):
            if line.strip() and pattern.match(line.split()[0]):
                parts = line.split()
                ip = parts[0]
                mac = parts[1]

                device = {
                    "ip": ip,
                    "mac": mac,
                }
                devices.append(device)

        return devices

    except Exception as e:
        return [{"error": f"Error al procesar la línea: {line}, {e}"}]


def start_capture(
    command_filter,
):
    if command_filter == "":
        custom_command = (
            "(tcp or udp) and (port http or https or smtp or ssh or ftp or telnet)"
        )
    else:
        custom_command = command_filter

    base_command = [
        "sudo",
        "tcpdump",
        # "-n"   # Muestra el trafico los host en formato de ip y no de dominio
        "-l",
        "-c",
        "100",
        "-i",
        "eth0",  # Hay que sacar la info de la interfaz de red donde se instale el sistema
    ]

    # Valores personalizados que pueden concatenarse
    custom_values = [
        custom_command,
    ]

    end_command = [
        "-tttt",
        "-q",
        "-v",
    ]

    # Concatenar las dos partes del comando
    command = base_command + custom_values + end_command

    print("filtro creado >", command_filter)
    print("Comando > ", command)

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True
    )

    packet_count = 0

    for line in process.stdout:
        if "ARP" in line:
            arp_info = line.strip().split(",")
            arp_parts = arp_info[0].split(" ")
            time = " ".join(arp_parts[:2])
            time_formatted = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            src_ip_domain = ""
            src_port = ""
            dst_ip_domain = ""
            dst_port = ""
            protocol = ""
            info = " ".join(arp_info[2:])
            yield f"data: {time_formatted} {src_ip_domain}:{src_port} > {dst_ip_domain}:{dst_port} {protocol} {info}\n\n"
        else:
            line2 = process.stdout.readline().strip()

            if not line2:
                break

            combined_line = line.strip() + " " + line2.strip()

        parts = []
        parenthesis_count = 0
        current_part = ""

        for char in combined_line:
            if char == "(":
                parenthesis_count += 1
            elif char == ")":
                parenthesis_count -= 1

            if parenthesis_count > 0:
                current_part += char
            else:
                if char == " " and current_part:
                    parts.append(current_part)
                    current_part = ""
                else:
                    current_part += char

        if current_part:
            parts.append(current_part)

        if len(parts) >= 6:
            time = " ".join(parts[:2])
            time_formatted = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            info = parts[3]

            info_parts = parts[3].rsplit(",", 6)
            info_protocol = info_parts[5].rsplit(" ", 2)
            protocol = info_protocol[1]

            src_parts = parts[4].rsplit(".", 1)
            src_ip_domain = src_parts[0]
            src_port = src_parts[1] if len(src_parts) > 1 else None

            dst_parts = parts[6].rsplit(".", 1)
            dst_ip_domain = dst_parts[0]
            dst_port = dst_parts[1].rstrip(":") if len(dst_parts) > 1 else None

            packet_count += 1

            # Emitir solo un cierto número de paquetes
            if packet_count >= 30:
                break

            yield f"data: {time_formatted} {src_ip_domain}:{src_port} > {dst_ip_domain}:{dst_port} {protocol} {info}\n\n"

    # Después de salir del bucle de captura, cerrar la conexión EventSource
    yield "event: close\n\n"


def pre_start_capture():
    custom_command = (
        "(tcp or udp) and (port http or https or smtp or ssh or ftp or telnet)"
    )

    base_command = [
        "sudo",
        "tcpdump",
        # "-n"   # Muestra el trafico los host en formato de ip y no de dominio
        "-l",
        "-c",
        "100",
        "-i",
        "eth0",  # Sacar la info de la interfaz de red donde se instale el sistema
    ]

    custom_values = [
        custom_command,
    ]

    end_command = [
        "-tttt",
        "-q",
        "-v",
    ]

    # Concatenar las dos partes del comando
    command = base_command + custom_values + end_command

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True
    )

    packet_count = 0

    for line in process.stdout:
        if "ARP" in line:
            arp_info = line.strip().split(",")
            arp_parts = arp_info[0].split(" ")
            time = " ".join(arp_parts[:2])
            time_formatted = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            src_ip_domain = ""
            src_port = ""
            dst_ip_domain = ""
            dst_port = ""
            protocol = ""
            info = " ".join(arp_info[2:])
            yield f"data: {time_formatted} {src_ip_domain}:{src_port} > {dst_ip_domain}:{dst_port} {protocol} {info}\n\n"
        else:
            line2 = process.stdout.readline().strip()

            if not line2:
                break

            combined_line = line.strip() + " " + line2.strip()

        parts = []
        parenthesis_count = 0
        current_part = ""

        for char in combined_line:
            if char == "(":
                parenthesis_count += 1
            elif char == ")":
                parenthesis_count -= 1

            if parenthesis_count > 0:
                current_part += char
            else:
                if char == " " and current_part:
                    parts.append(current_part)
                    current_part = ""
                else:
                    current_part += char

        if current_part:
            parts.append(current_part)

        if len(parts) >= 6:
            time = " ".join(parts[:2])
            time_formatted = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            info = parts[3]

            info_parts = parts[3].rsplit(",", 6)
            info_protocol = info_parts[5].rsplit(" ", 2)
            protocol = info_protocol[1]

            src_parts = parts[4].rsplit(".", 1)
            src_ip_domain = src_parts[0]
            src_port = src_parts[1] if len(src_parts) > 1 else None

            dst_parts = parts[6].rsplit(".", 1)
            dst_ip_domain = dst_parts[0]
            dst_port = dst_parts[1].rstrip(":") if len(dst_parts) > 1 else None

            packet_count += 1

            # Emitir solo un cierto número de paquetes
            if packet_count >= 100:
                break

            yield f"data: {time_formatted} {src_ip_domain}:{src_port} > {dst_ip_domain}:{dst_port} {protocol} {info}\n\n"

    # Después de salir del bucle de captura, cerrar la conexión EventSource
    yield "event: close\n\n"


def delete_rule(regla_content_id, id_regla):
    try:
        if regla_content_id:
            rule_detail = modelFirewallDetail.getDetailById(regla_content_id)
            rule_string = rule_detail[1]
            estado_detail = rule_detail[2]

            rule_detail_name = rule_string.split(" -m comment --comment ")[1].replace(
                "'", ""
            )

            if estado_detail == 1:
                if "INPUT" in rule_string:
                    direccion = "INPUT"
                elif "OUTPUT" in rule_string:
                    direccion = "OUTPUT"

                salida_iptables = subprocess.check_output(
                    [
                        "sudo",
                        "iptables",
                        "-L",
                        direccion,
                        "--line-numbers",
                        "-n",
                    ]
                )

                iptables_rules_matched(salida_iptables, rule_detail_name, direccion)

            modelFirewallDetail.deleteDetailById(regla_content_id)

        else:
            rule_db_filter = modelFirewall.getRuleById(id_regla)

            rule_name = rule_db_filter[2]
            tipo_regla = rule_db_filter[3]

            numero_data = int(rule_db_filter[5])

            detail_rules = modelFirewallDetail.getRulesDetailsById(id_regla)

            if numero_data == 1:
                for detail_rule in detail_rules:
                    rule_string = detail_rule[1]

                    if tipo_regla == "contenido" or tipo_regla == "dominio":
                        if "INPUT" in rule_string:
                            direccion = "INPUT"
                        elif "OUTPUT" in rule_string:
                            direccion = "OUTPUT"

                    else:
                        rule_delete = (
                            f"sudo {rule_string.replace('ufw ', 'ufw delete ')}"
                        )

                        print(rule_delete)

                        subprocess.run(
                            shlex.split(f"{rule_delete}"),
                            input="y\n",
                            text=True,
                            capture_output=True,
                        )

                if tipo_regla == "contenido" or tipo_regla == "dominio":
                    salida_iptables = subprocess.check_output(
                        [
                            "sudo",
                            "iptables",
                            "-L",
                            direccion,
                            "--line-numbers",
                            "-n",
                        ]
                    )

                    iptables_rules_matched(salida_iptables, rule_name, direccion)

            modelFirewallDetail.deleteRuleDetail(id_regla)
            modelFirewall.deleteRule(id_regla)

        return "Regla Eliminada Correctamente"
    except subprocess.CalledProcessError as e:
        return f"Error al obtener el número de la regla: {e}"


def deactivate_activate_rule(id_regla, regla_content_id):
    try:
        if regla_content_id:
            rule_detail = modelFirewallDetail.getDetailById(regla_content_id)
            rule_string = rule_detail[1]
            estado_detail = rule_detail[2]

            rule_detail_name = rule_string.split(" -m comment --comment ")[1].replace(
                "'", ""
            )

            if estado_detail == 1:
                if "INPUT" in rule_string:
                    direccion = "INPUT"
                elif "OUTPUT" in rule_string:
                    direccion = "OUTPUT"

                salida_iptables = subprocess.check_output(
                    [
                        "sudo",
                        "iptables",
                        "-L",
                        direccion,
                        "--line-numbers",
                        "-n",
                    ]
                )

                iptables_rules_matched(salida_iptables, rule_detail_name, direccion)
                modelFirewallDetail.updateDetail(0, regla_content_id)

                return "Regla Desactivada"

            elif estado_detail == 0:
                rule = f"sudo {rule_string}"
                subprocess.run(shlex.split(f"{rule}"))

                modelFirewallDetail.updateDetail(1, regla_content_id)

                return "Regla Activa"

        elif id_regla and not regla_content_id:
            rule_db_filter = modelFirewall.getRuleById(id_regla)

            rule_name = rule_db_filter[2]
            numero_data = int(rule_db_filter[5])
            tipo_regla = rule_db_filter[3]

            detail_rules = modelFirewallDetail.getRulesDetailsById(id_regla)
            if rule_db_filter:
                if numero_data == 1:
                    for detail_rule in detail_rules:
                        rule_detail_id = detail_rule[0]
                        rule_string = detail_rule[1]

                        if tipo_regla == "contenido" or tipo_regla == "dominio":
                            if "INPUT" in rule_string:
                                direccion = "INPUT"
                            elif "OUTPUT" in rule_string:
                                direccion = "OUTPUT"

                        else:
                            rule_delete = (
                                f"sudo {rule_string.replace('ufw ', 'ufw delete ')}"
                            )

                            print(rule_delete)

                            subprocess.run(
                                shlex.split(f"{rule_delete}"),
                                input="y\n",
                                text=True,
                                capture_output=True,
                            )

                        modelFirewallDetail.updateDetail(0, rule_detail_id)

                    if tipo_regla == "contenido" or tipo_regla == "dominio":
                        salida_iptables = subprocess.check_output(
                            [
                                "sudo",
                                "iptables",
                                "-L",
                                direccion,
                                "--line-numbers",
                                "-n",
                            ]
                        )

                        iptables_rules_matched(salida_iptables, rule_name, direccion)

                    modelFirewall.updateRule(0, id_regla)
                    return "Regla Desactivada"
                elif numero_data == 0:
                    for detail_rule in detail_rules:
                        rule_detail_id = detail_rule[0]
                        rule_string = detail_rule[1]

                        rule = f"sudo {rule_string}"
                        subprocess.run(shlex.split(f"{rule}"))

                        modelFirewallDetail.updateDetail(1, rule_detail_id)
                    modelFirewall.updateRule(1, id_regla)
                    return "Regla Activa"
            else:
                return "No se encontró una regla con ese nombre"

        return "El nombre de la regla no puede ser None o vacío"
    except subprocess.CalledProcessError as e:
        return f"Error al obtener el número de la regla: {e}"


def iptables_rules_matched(salida_iptables, name_iptable, direccion):
    reglas = salida_iptables.decode("utf-8").splitlines()
    id_iptable_delete = None

    consulta_formateada = "\n".join(reglas[2:])

    for line in consulta_formateada.splitlines():
        id_iptable_rule = line.split()[0]
        if name_iptable in line:
            if id_iptable_delete is None:
                id_iptable_delete = id_iptable_rule

            rule_delete = f"sudo iptables -D {direccion} {id_iptable_delete}"

            subprocess.run(
                shlex.split(f"{rule_delete}"),
            )

    return "Regla Eliminada"


def execute_command(command):
    # Ejecutar el comando y capturar la salida
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout


def get_domain_info(domain):
    command = f"nslookup {domain}"

    output = execute_command(command)
    # Dividir las líneas de salida
    lines = output.split("\n")

    ip_addresses = []

    for line in lines[2:]:
        if "Address:" in line:
            parts = line.split(":")
            if len(parts) == 2:
                ip_addresses.append(parts[1].strip())

    return ip_addresses


# Plataformas con ips dinamicas
plataformas_dinamicas = {
    "redes_sociales": [
        "www.tiktok.com",
    ]
}

# Plataformas con ips estaticas
plataformas = {
    "redes_sociales": [
        "facebook.com",
        "twitter.com",
        "instagram.com",
        "ec.linkedin.com",
        "linkedin.com",
        "pinterest.com",
        "www.pinterest.com",
        "snapchat.com",
        "tiktok.com",
        "x.com",
    ],
    "videojuegos": [
        "steampowered.com",
        "epicgames.com",
        "www.epicgames.com",
        "store.epicgames.com",
        "origin.com",
        "uplay.com",
        "gog.com",
    ],
    # "musica": ["spotify.com", "apple.com/music", "youtube.com/music", "googleplay.com/music", "pandora.com"],
    "musica": [
        "spotify.com",
        "apple.com",
        "www.youtube.com",
        "googleplay.com",
        "pandora.com",
    ],
    # "streaming": ["netflix.com", "hulu.com", "amazon.com/prime-video", "disneyplus.com", "hbo.com"],
    "streaming": [
        "netflix.com",
        "hulu.com",
        "amazon.com",
        "disneyplus.com",
        "hbo.com",
    ],
    # "lectura": ["amazon.com/kindle", "google.com/books", "scribd.com", "wattpad.com", "goodreads.com"],
    "lectura": ["amazon.com", "scribd.com", "wattpad.com", "goodreads.com"],
    "educacion": [
        "coursera.org",
        "udemy.com",
        "khanacademy.org",
        "edx.org",
        "udacity.com",
    ],
    # "podcast": ["apple.com/podcasts", "spotify.com/podcasts", "google.com/podcasts", "stitcher.com", "podbean.com"],
    "podcast": ["apple.com", "spotify.com", "stitcher.com", "podbean.com"],
    # "mensajeria": ["whatsapp.com", "facebook.com/messages", "telegram.org", "slack.com", "discord.com"],
    "mensajeria": [
        "whatsapp.com",
        "facebook.com",
        "telegram.org",
        "slack.com",
        "discord.com",
    ],
    "mailing": [
        "gmail.com",
        "outlook.com",
        "yahoo.com",
        "aol.com",
        "protonmail.com",
    ],
    # "blogging": ["wordpress.com", "blogger.com", "tumblr.com", "medium.com", "github.com/blogs"],
    "blogging": ["wordpress.com", "blogger.com", "tumblr.com", "medium.com"],
    # "imagenes": ["google.com/images", "flickr.com", "instagram.com", "unsplash.com", "imgur.com"],
    "imagenes": ["flickr.com", "unsplash.com", "imgur.com"],
    "ecommerce": [
        "amazon.com",
        "ebay.com",
        "walmart.com",
        "target.com",
        "etsy.com",
    ],
    "pago": ["paypal.com", "square.com", "stripe.com", "authorize.net"],
    "crm": [
        "salesforce.com",
        "zoho.com",
        "hubspot.com",
        "marketo.com",
        "pardot.com",
    ],
    # "publicidad_digital": ["google.com/ads", "facebook.com/business", "instagram.com/business", "pinterest.com/business", "twitter.com/business"],
    "redes_profesionales": ["linkedin.com", "indeed.com", "glassdoor.com"],
    # "trabajo_colaborativo": ["google.com/docs", "microsoft.com/office-online", "dropbox.com"],
    "trabajo_colaborativo": ["dropbox.com"],
    # "videoconferencias": ["zoom.us", "teams.microsoft.com", "google.com/meet"],
    "videoconferencias": ["zoom.us", "teams.microsoft.com"],
    "apuestas": [
        "bet365.com",
        # "bwin.com",
        "www.bwin.com",
        # "888sport.com",
        "www.888sport.com",
        "williamhill.com",
        "betfair.com",
        "unibet.com",
        "ladbrokes.com",
        "coral.co.uk",
        "stanjames.com",
        "skybet.com",
    ],
    "video": ["youtube.com", "vimeo.com", "dailymotion.com", "twitch.tv"],
}


def clean_cache():
    # Obtener los datos del cuerpo de la solicitud
    ip_remota = "192.168.0.105"
    puerto = 5335
    usuario = "kali"
    password = "kali"
    comandos = [
        "pkill firefox",
        "rm -rf ~/.cache/mozilla/firefox/*.default/cache2/*",
        "rm -rf ~/.cache/google-chrome/Default/Cache/*",
        "firefox &",  # Se puede ejecutar como usuario normal
    ]

    # Verificar que todos los datos necesarios estén presentes
    if ip_remota and usuario and password:
        resultados = []
        for comando in comandos:
            # Enviar la orden SSH
            salida, error = enviar_orden_ssh(
                ip_remota, puerto, usuario, password, comando
            )
            resultados.append({"comando": comando, "salida": salida, "error": error})
        return jsonify(resultados), 200
    else:
        return jsonify({"mensaje": "Faltan datos en la solicitud"}), 400


def enviar_orden_ssh(ip_remota, puerto, usuario, password, comando):
    try:
        # Configura la conexión SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Conéctate a la máquina remota
        ssh_client.connect(ip_remota, port=puerto, username=usuario, password=password)

        # Ejecuta el comando en la máquina remota
        stdin, stdout, stderr = ssh_client.exec_command(comando)

        # Lee la salida del comando (si es necesario)
        salida = stdout.read().decode()
        error = stderr.read().decode()

        # Cierra la conexión SSH
        ssh_client.close()

        # Retorna la salida y el error
        return salida, error

    except Exception as e:
        return "", str(e)


def allow_connections(
    accion_regla,
    tipo_regla,
    ip_addr,
    domain,
    port,
    protocol,
    entry,
    direction,
    netmask,
    ip_dest,
    dest_netmask,
    portStart,
    portLimit,
    comment,
    content_tp,
):
    try:
        if protocol == "tcp/udp":
            protocol = ""

        ip_dest = "any"

        if entry == "in":
            direction = "from"
        elif entry == "out":
            direction = "to"
            ip_dest = ""

        rule = f"sudo ufw {accion_regla}"
        fecha_creacion = datetime.now()

        rulesTypeContent = []

        if tipo_regla == "dominio" or tipo_regla == "contenido":
            if accion_regla == "allow":
                accion_regla = "ACCEPT"
            elif accion_regla == "reject":
                accion_regla = "REJECT"

            if entry == "in":
                entry = "INPUT"
                direction = "-s"
            elif entry == "out":
                entry = "OUTPUT"
                direction = "-d"

        if content_tp and not domain:
            for platform in content_tp:
                if platform in plataformas:
                    platform_name = platform.lower().replace("_", " ").title()
                    rulesContent = []
                    comment_content = f"{comment} - {platform_name}"
                    for domainPlataform in plataformas[platform]:
                        rule = f"sudo iptables -I {entry} 1 {direction} {domainPlataform} -j {accion_regla}"

                        rule += f" -m comment --comment '{comment_content} - {domainPlataform}'"
                        rulesContent.append(rule)

                        subprocess.run(shlex.split(f"{rule}"))

                    for domainPlataform in plataformas_dinamicas[platform]:
                        ip_domain = verify_domain_dynamic(domainPlataform)

                        if isinstance(ip_domain, list):
                            print("iprint es una lista:", ip_domain)
                            for ip in ip_domain:
                                print("")
                                rule = f"sudo iptables -I {entry} 1 {direction} {ip} -j {accion_regla}"

                                rule += f" -m comment --comment '{comment_content} - {domainPlataform}'"
                                rulesContent.append(rule)
                                subprocess.run(shlex.split(f"{rule}"))

                        elif isinstance(ip_domain, str):
                            rule = f"sudo iptables -I {entry} 1 {direction} {ip_domain} -j {accion_regla}"

                            rule += f" -m comment --comment '{comment_content} - {domainPlataform}'"
                            rulesContent.append(rule)

                            subprocess.run(shlex.split(f"{rule}"))

                    rulesTypeContent.append((rulesContent, comment_content))
                else:
                    print(f"Invalid platform: {platform_name}")

        elif domain:
            rules_domain_dynamic = []

            comment_domain = f"{comment} - {domain}"

            for categorias in plataformas:
            
                print(categorias)

                for domain in plataformas[categorias]:
                    rule = (
                        f"sudo iptables -I {entry} 1 {direction} {domain} -j {accion_regla}"
                    )

                    rule += f" -m comment --comment '{comment_domain}'"

                    subprocess.run(shlex.split(f"{rule}"))

                for domain in plataformas_dinamicas[platform]:
                    comment_content = f"{comment} - {platform_name}"

                    ip_domain = verify_domain_dynamic(domainPlataform)

                    if isinstance(ip_domain, list):
                        print("iprint es una lista:", ip_domain)
                        for ip in ip_domain:
                            rule = f"sudo iptables -I {entry} 1 {direction} {ip} -j {accion_regla}"

                            rule += f" -m comment --comment '{comment_domain}'"
                            rules_domain_dynamic.append(rule)
                            subprocess.run(shlex.split(f"{rule}"))

                    elif isinstance(ip_domain, str):
                        rule = f"sudo iptables -I {entry} 1 {direction} {ip_domain} -j {accion_regla}"

                        rule += f" -m comment --comment '{comment_domain}'"

                        subprocess.run(shlex.split(f"{rule}"))

        elif (port or portStart or portLimit) and ip_addr and not domain:
            if ip_addr and netmask:
                ip_addr += f"/{netmask}"
            if ip_dest and dest_netmask:
                ip_dest += f"/{dest_netmask}"

            if entry and direction and ip_addr and portStart and portLimit and protocol:
                rule += f" {entry} {direction} {ip_addr} port {portStart}:{portLimit} proto {protocol}"
                rule += f" comment '{comment}'"

            elif (
                entry
                and direction
                and ip_addr
                and portStart
                and ip_dest
                and portLimit
                and protocol
            ):
                rule += f" {entry} {direction} {ip_addr} port {portStart} to {ip_dest} port {portLimit} proto {protocol} comment '{comment}'"

            elif (
                entry and direction and ip_addr and portStart and ip_dest and portLimit
            ):
                rule += f" {entry} {direction} {ip_addr} port {portStart} to {ip_dest} port {portLimit} comment '{comment}'"

            elif entry and direction and ip_addr and ip_dest and port and protocol:
                rule += f" {entry} {direction} {ip_addr} to {ip_dest} port {port} proto {protocol} comment '{comment}'"

            elif (
                entry and direction and ip_addr and portStart and portLimit and protocol
            ):
                rule += f" {entry} {direction} {ip_addr} port {portStart} to any port {portLimit} proto {protocol} comment '{comment}'"

            elif (
                entry and direction and portStart and ip_dest and portLimit and protocol
            ):
                rule += f" {entry} {direction} any port {portStart} to {ip_dest} port {portLimit} proto {protocol} comment '{comment}'"

            elif entry and direction and portStart and ip_dest and portLimit:
                rule += f" {entry} {direction} any port {portStart} to {ip_dest} port {portLimit} comment '{comment}'"

            elif entry and direction and ip_addr and portStart and portLimit:
                rule += f" {entry} {direction} {ip_addr} port {portStart} to any port {portLimit} comment '{comment}'"

            elif entry and direction and ip_addr and portLimit and protocol:
                rule += f" {entry} {direction} {ip_addr} to any port {portLimit} proto {protocol} comment '{comment}'"

            elif entry and direction and ip_addr and portStart and ip_dest and protocol:
                rule += f" {entry} {direction} {ip_addr} port {portStart} to {ip_dest} proto {protocol} comment '{comment}'"

            elif entry and direction and ip_addr and portStart and protocol:
                rule += f" {entry} {direction} {ip_addr} port {portStart} to any proto {protocol} comment '{comment}'"

            elif (
                entry and direction and ip_dest and portStart and portLimit and protocol
            ):
                rule += f" {entry} {direction} any port {portStart} to {ip_dest} port {portLimit} proto {protocol} comment '{comment}'"

            elif entry and direction and ip_dest and portLimit and protocol:
                rule += f" {entry} {direction} any to {ip_dest} port {portLimit} proto {protocol} comment '{comment}'"

            elif entry and direction and portStart and ip_dest and portLimit:
                rule += f" {entry} {direction} any port {portStart} to {ip_dest} port {portLimit} comment '{comment}'"

            elif entry and direction and ip_addr and portStart and ip_dest:
                rule += f" {entry} {direction} {ip_addr} port {portStart} to {ip_dest} comment '{comment}'"

            elif entry and direction and ip_addr and portStart:
                rule += f" {entry} {direction} {ip_addr} port {portStart} to any comment '{comment}'"

            elif entry and direction and ip_addr and portLimit:
                rule += f" {entry} {direction} {ip_addr} to any port {portLimit} comment '{comment}'"

            elif entry and direction and ip_dest and portLimit:
                rule += f" {entry} {direction} any to {ip_dest} port {portLimit} comment '{comment}'"

            elif entry and direction and ip_addr and port and protocol:
                rule += f" {entry} {direction} {ip_addr} port {port} proto {protocol} comment '{comment}'"

            elif entry and direction and ip_addr and portStart and portLimit:
                rule += f" {entry} {direction} {ip_addr} port {portStart}:{portLimit} comment '{comment}'"

            elif entry and direction and ip_addr and ip_dest and port:
                rule += f" {entry} {direction} {ip_addr} to {ip_dest} port {port} comment '{comment}'"

            elif entry and direction and ip_addr and ip_dest and port:
                rule += f" {entry} {direction} {ip_addr} to {ip_dest} {port} comment '{comment}'"

            elif entry and direction and ip_dest and port and protocol:
                rule += f" {entry} {direction} any to {ip_dest} port {port} proto {protocol} comment '{comment}'"

            elif entry and direction and ip_addr and port and protocol:
                rule += f" {entry} {direction} {ip_addr} port {port} proto {protocol} comment '{comment}'"

            elif entry and direction and ip_addr and port:
                rule += (
                    f" {entry} {direction} {ip_addr} port {port} comment '{comment}'"
                )

            elif entry and direction and ip_dest and port:
                rule += f" {entry} {direction} any to {ip_dest} port {port} comment '{comment}'"

            subprocess.run(shlex.split(f"{rule}"))

        # IPs
        elif ip_addr and not domain:
            if ip_addr and netmask:
                ip_addr += f"/{netmask}"
            if ip_dest and dest_netmask:
                ip_dest += f"/{dest_netmask}"

            if entry and direction and ip_addr and ip_dest and protocol:
                rule += f" {entry} {direction} {ip_addr} to {ip_dest} proto {protocol} comment '{comment}'"

            elif entry and direction and ip_addr and protocol:
                rule += f" {entry} {direction} {ip_addr} proto {protocol} comment '{comment}'"

            elif entry and direction and ip_dest and protocol:
                rule += f" {entry} {direction} any to {ip_dest} proto {protocol} comment '{comment}'"

            elif entry and direction and ip_addr and ip_dest:
                rule += (
                    f" {entry} {direction} {ip_addr} to {ip_dest} comment '{comment}'"
                )

            elif entry and direction and ip_addr:
                rule += f" {entry} {direction} {ip_addr} comment '{comment}'"

            elif entry and direction and ip_dest:
                rule += f" {entry} {direction} any to {ip_dest} comment '{comment}'"

            subprocess.run(shlex.split(f"{rule}"))

        # Port
        elif port or portStart or portLimit and not domain:
            if entry and direction and portStart and portLimit and protocol:
                rule += f" {entry} {direction} any port {portStart}:{portLimit} proto {protocol} comment '{comment}'"

            elif entry and direction and port and protocol:
                rule += f" {entry} {direction} any port {port} proto {protocol} comment '{comment}'"

            elif entry and portStart and portLimit and protocol:
                rule += (
                    f" {entry} {portStart}:{portLimit}/{protocol} comment '{comment}'"
                )

            elif entry and port and protocol:
                rule += f" {entry} {port}/{protocol} comment '{comment}'"

            elif entry and direction and port:
                rule += f" {entry} {direction} any port {port} comment '{comment}'"

            elif entry and port:
                rule += f" {entry} {port} comment '{comment}'"

            subprocess.run(shlex.split(f"{rule}"))

        print(rule)

        if rulesTypeContent:
            for rulesContentPlatform in rulesTypeContent:
                firewall = Firewall(
                    0,
                    rulesContentPlatform[1],
                    tipo_regla,
                    fecha_creacion,
                    1,
                    current_user.id,
                )

                firewall = modelFirewall.insertRule(firewall)
                id_rule = firewall.id

                # Iteramos sobre las reglas de la plataforma actual
                for rule in rulesContentPlatform[0]:
                    save_rule = format_rule_save(rule)
                    firewallDetail = FirewallDetail(0, id_rule, save_rule, 1)
                    modelFirewallDetail.insertRuleDetail(firewallDetail)

        elif domain:
            firewall = Firewall(
                0,
                comment_domain,
                tipo_regla,
                fecha_creacion,
                1,
                current_user.id,
            )
            firewall = modelFirewall.insertRule(firewall)
            id_rule = firewall.id

            if rules_domain_dynamic:
                for domain_rule_ip in rules_domain_dynamic:
                    save_rule = format_rule_save(domain_rule_ip)
                    firewallDetail = FirewallDetail(0, id_rule, save_rule, 1)
                    modelFirewallDetail.insertRuleDetail(firewallDetail)
            else:
                save_rule = format_rule_save(rule)
                firewallDetail = FirewallDetail(0, id_rule, save_rule, 1)
                modelFirewallDetail.insertRuleDetail(firewallDetail)

        else:
            firewall = Firewall(
                0,
                comment,
                tipo_regla,
                fecha_creacion,
                1,
                current_user.id,
            )
            firewall = modelFirewall.insertRule(firewall)
            id_rule = firewall.id

            save_rule = format_rule_save(rule)
            firewallDetail = FirewallDetail(0, id_rule, save_rule, 1)
            modelFirewallDetail.insertRuleDetail(firewallDetail)

        return "Regla creada correctamente"
    except subprocess.CalledProcessError:
        return "Error al permitir el puerto."


# Ejecutara unicamente dominios que las ips sean dinamicas
def verify_domain_dynamic(domain):
    ips_set = set()  # Conjunto para almacenar las IPs únicas
    ips = []
    ips_sorted = None

    for _ in range(5):  # Ejecutar el comando cinco veces
        salida = subprocess.check_output(["dig", "+short", domain])
        ips_domain = salida.decode("utf-8").splitlines()

        for ip in ips_domain:
            match = re.match(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", ip)
            if match:
                ips.append(ip)

        ips_set.update(ips)  # Agregar las IPs únicas al conjunto

    first_octets = set(ip.split(".")[0] for ip in ips_set)
    second_octets = set(ip.split(".")[1] for ip in ips_set)
    third_octets = set(ip.split(".")[2] for ip in ips_set)
    if len(first_octets) == 1:
        common_first_octets = first_octets.pop()
        common_second_octets = second_octets.pop()
        common_third_octets = third_octets.pop()
        common_ip = (
            f"{common_first_octets}.{common_second_octets}.{common_third_octets}.0/24"
        )
        print(
            "Todas las direcciones IP tienen los mismos tres primeros octetos:",
            common_ip,
        )

        return common_ip
    else:
        # Convertir el conjunto a una lista y ordenarla
        ips_sorted = sorted(list(ips_set))

    # Imprimir las IPs ordenadas
    if ips_sorted:
        for ip in ips_sorted:
            """ rule = f"sudo iptables -I OUTPUT 1 -d {ip} -j REJECT"

            rule += " -m comment --comment 'bloqueo - prubish'"

            subprocess.run(shlex.split(f"{rule}")) """

            print(ip)
        return ips_sorted


def allow_connections_detail(
    id_regla,
    regla_name,
    accion_regla,
    entry,
    domain,
):
    try:
        if entry == "INPUT":
            direction = "-s"
        elif entry == "OUTPUT":
            direction = "-d"

        rulesSavedDomain = []

        detail_rules = modelFirewallDetail.getRulesDetailsById(id_regla)

        for detail_rule in detail_rules:
            rule_save_string = detail_rule[1]
            rule_saved_parts = rule_save_string.split(" -m comment --comment ")
            rule_save_command = rule_saved_parts[0]
            rulesSavedDomain.append(rule_save_command)

        comment_domain = f"{regla_name} - {domain}"
        rule = f"sudo iptables -I {entry} 1 {direction} {domain} -j {accion_regla}"

        rule += f" -m comment --comment '{comment_domain}'"

        save_rule = format_rule_save(rule)
        rule_parts = save_rule.split(" -m comment --comment ")
        rule_command = rule_parts[0]

        if not any(rule_command in detail_rule for detail_rule in rulesSavedDomain):
            subprocess.run(shlex.split(f"{rule}"))
            firewallDetail = FirewallDetail(0, id_regla, save_rule, 1)
            modelFirewallDetail.insertRuleDetail(firewallDetail)

        return "Regla creada correctamente"
    except subprocess.CalledProcessError:
        return "Error al permitir el puerto."


def format_rule_save(rule):
    formatted_rule = rule.replace("sudo ", "")

    return formatted_rule


def generate_content_domain(content, prefix):
    content_domain = f"{prefix}"
    plataforms = ""
    for platform in content:
        if platform in plataformas:
            domains = [
                f" {domain} or" if index >= 0 else f" {domain}"
                for index, domain in enumerate(plataformas[platform])
            ]
            domain_string = "".join(domains)
            content_domain += domain_string
            plataforms += f"{platform} -"

    content_domain = content_domain.rstrip(" or")
    plataforms = plataforms.rstrip(" -")
    return content_domain, plataforms


def save_filter(
    name_filter,
    type_ip,
    type_domain,
    type_content,
    type_mac,
    type_port,
    type_proto_red,
    ip_addr,
    ip_dest,
    content_dst,
    port_red_src,
    port_red_dst,
    port_src,
    port_dst,
    packet_protocol,
    mac_addr,
    mac_dest,
    generalIp,
    generalDomain,
    generalContent,
    generalPort,
    generalPortRed,
    logic_operator_ip,
    logic_operator_mac,
    logic_operator_mac_port,
    logic_operator_proto_red_proto,
):
    try:
        type_filter = ""
        filter_values = [
            type_ip,
            type_domain,
            type_content,
            type_mac,
            type_port,
            type_proto_red,
        ]

        # Filtrar los valores para eliminar los vacíos
        filtered_values = [value for value in filter_values if value]

        type_filter = " con ".join(filtered_values)

        patron_coma = re.compile(r",\s*")

        # Variables Custom
        ips_custom = ""
        port_custom = ""
        protocol_custom = ""
        command_filter = ""
        plataforms = ""
        contents_filter = ""

        # Manejo de Contenido
        if content_dst:
            content_domain_dst, plataforms_dst = generate_content_domain(
                content_dst, "dst host"
            )
            contents_filter = f"{content_domain_dst}"
            plataforms = f"{plataforms_dst}"

        elif generalContent:
            content_domain_general, plataforms_general = generate_content_domain(
                generalContent, "host"
            )

            contents_filter = f"{content_domain_general}"
            plataforms = f"{plataforms_general}"

        elif generalDomain:
            domains_general = patron_coma.sub(" or ", generalDomain)
            general_domain = f"host {domains_general}"
            ips_custom = general_domain

        # Manejo de ips
        if ip_addr:
            if patron_coma.search(ip_addr):
                src_ips = patron_coma.sub(" or ", ip_addr)
                src_host = f"src host {src_ips}"
            else:
                src_host = f"src host {ip_addr}"

        if ip_dest:
            if patron_coma.search(ip_dest):
                dst_ips = patron_coma.sub(" or ", ip_dest)
                dst_host = f"dst host {dst_ips}"
            else:
                dst_host = f"dst host {ip_dest}"

        if generalIp:
            if patron_coma.search(generalIp):
                general_ips = patron_coma.sub(" or ", generalIp)
                general_host = f"host {general_ips}"
            else:
                general_host = f"host {generalIp}"

        # Manejo de MACS
        if mac_addr:
            if patron_coma.search(mac_addr):
                src_macs = patron_coma.sub(" or ", mac_addr)
                src_ether = f"ether src {src_macs}"
            else:
                src_ether = f"ether src {mac_addr}"

        if mac_dest:
            if patron_coma.search(mac_dest):
                dst_macs = patron_coma.sub(" or ", mac_dest)
                dst_ether = f"ether dst {dst_macs}"
            else:
                dst_ether = f"ether dst {mac_dest}"

        if ip_addr and ip_dest and mac_addr and mac_dest:
            ips_custom = f"{src_host} {logic_operator_ip} {dst_host} or {src_ether} {logic_operator_mac} {dst_ether}"
        elif ip_addr and ip_dest and mac_addr:
            ips_custom = f"{src_host} {logic_operator_ip} {dst_host} or {src_ether}"
        elif ip_addr and ip_dest and mac_dest:
            ips_custom = f"{src_host} {logic_operator_ip} {dst_host} or {dst_ether}"
        elif mac_addr and mac_dest and generalIp:
            ips_custom = (
                f"{src_ether} {logic_operator_mac} {dst_ether} or {general_host}"
            )
        elif mac_addr and mac_dest and ip_addr:
            ips_custom = f"{src_ether} {logic_operator_mac} {dst_ether} or {src_host}"
        elif mac_addr and mac_dest and ip_dest:
            ips_custom = f"{src_ether} {logic_operator_mac} {dst_ether} or {dst_host}"
        elif ip_addr and mac_addr:
            ips_custom = f"{src_host} or {src_macs}"
        elif ip_addr and mac_dest:
            ips_custom = f"{src_host} or {dst_macs}"
        elif ip_dest and mac_addr:
            ips_custom = f"{dst_host} or {src_macs}"
        elif ip_dest and mac_dest:
            ips_custom = f"{dst_host} or {dst_macs}"
        elif mac_addr and generalIp:
            ips_custom = f"{src_ether} or {general_host}"
        elif mac_dest and generalIp:
            ips_custom = f"{dst_ether} or {general_host}"
        elif ip_addr and ip_dest:
            ips_custom = f"{src_host} {logic_operator_ip} {dst_host}"
        elif ip_addr:
            ips_custom = f"{src_host}"
        elif ip_dest:
            ips_custom = f"{dst_host}"
        elif generalIp:
            ips_custom = f"{general_host}"
        elif mac_addr and mac_dest:
            ips_custom = f"{src_ether} {logic_operator_mac} {dst_ether}"
        elif mac_addr:
            ips_custom = f"{src_ether}"
        elif mac_dest:
            ips_custom = f"{dst_ether}"

        # filtro general de ips, dominios o contenido
        if contents_filter:
            ips_custom = f"({contents_filter})"
        elif ips_custom:
            ips_custom = f"({ips_custom})"

        print(ips_custom)

        # Manejo de Puertos
        if port_src:
            if patron_coma.search(port_src):
                src_ports = patron_coma.sub(" or ", port_src)
                src_port = f"src port {src_ports}"
            else:
                src_port = f"src port {port_src}"

        if port_dst:
            if patron_coma.search(port_dst):
                dst_ports = patron_coma.sub(" or ", port_dst)
                dst_port = f"dst port {dst_ports}"
            else:
                dst_port = f"dst port {port_dst}"

        if generalPort:
            if patron_coma.search(generalPort):
                general_ports = patron_coma.sub(" or ", generalPort)
                general_port = f"port {general_ports}"
            else:
                general_port = f"port {generalPort}"

        if port_red_src:
            combined_port_red_src = " or ".join(port_red_src)
            src_port_red = f"src port {combined_port_red_src}"

        if port_red_dst:
            combined_port_red_dst = " or ".join(port_red_dst)
            dst_port_red = f"dst port {combined_port_red_dst}"

        if generalPortRed:
            combined_port_red_general = " or ".join(generalPortRed)
            general_port_red = f"port {combined_port_red_general}"

        # Puertos
        if port_src and port_dst and port_red_src and port_red_dst:
            port_custom = (
                f"({src_port} or {dst_port} or {src_port_red} or {dst_port_red})"
            )
        elif port_src and port_dst and port_red_src:
            port_custom = f"({src_port} or {dst_port} or {src_port_red})"
        elif port_src and port_dst and port_red_dst:
            port_custom = f"({src_port} or {dst_port} or {dst_port_red})"
        elif port_red_src and port_red_dst and port_src:
            port_custom = f"({src_port_red} or {dst_port_red} or {src_port})"
        elif port_red_src and port_red_dst and port_dst:
            port_custom = f"({src_port_red} or {dst_port_red} or {dst_port})"
        elif port_src and port_dst and generalPortRed:
            port_custom = f"({src_port} or {dst_port} or {general_port_red})"
        elif port_red_src and port_red_dst and generalPort:
            port_custom = f"({src_port_red} or {dst_port_red} or {general_port})"
        # Doble dato
        elif generalPortRed and generalPort:
            port_custom = f"({general_port} or {general_port_red})"
        elif port_src and generalPortRed:
            port_custom = f"({src_port} or {general_port_red})"
        elif port_dst and generalPortRed:
            port_custom = f"({src_port} or {general_port_red})"
        elif port_red_src and generalPort:
            port_custom = f"({src_port_red} or {general_port})"
        elif port_red_dst and generalPort:
            port_custom = f"({src_port_red} or {general_port})"
        elif port_src and port_dst:
            port_custom = f"({src_port} or {dst_port})"
        elif port_red_src and port_red_dst:
            port_custom = f"({src_port_red} or {dst_port_red})"
        elif port_red_src and port_src:
            port_custom = f"({src_port_red} or {src_port})"
        elif port_red_src and port_dst:
            port_custom = f"({src_port_red} or {dst_port})"
        elif port_src and port_red_dst:
            port_custom = f"({dst_port_red} or {src_port})"
        elif port_red_dst and port_dst:
            port_custom = f"({dst_port_red} or {dst_port})"
        elif port_src:
            port_custom = f"({src_port})"
        elif port_dst:
            port_custom = f"({dst_port})"
        elif generalPort:
            port_custom = f"({general_port})"
        elif port_red_src:
            port_custom = f"({src_port_red})"
        elif port_red_dst:
            port_custom = f"({dst_port_red})"
        elif generalPortRed:
            port_custom = f"({general_port_red})"

        # Manejo de protocolos  ||  Siempre debe ir al final
        if packet_protocol == "tcp":
            protocol_custom = "(tcp)"
        elif packet_protocol == "udp":
            protocol_custom = "(udp)"
        elif packet_protocol == "tcp/udp":
            protocol_custom = "(tcp or udp)"

        # Unir elementos para formar el filtro
        if ips_custom and port_custom and protocol_custom:
            command_filter = f"{ips_custom} {logic_operator_mac_port} {port_custom} {logic_operator_proto_red_proto} {protocol_custom}"
        elif ips_custom and port_custom:
            command_filter = f"{ips_custom} {logic_operator_mac_port} {port_custom}"
        elif ips_custom and protocol_custom:
            command_filter = f"{ips_custom} {logic_operator_mac_port} {protocol_custom}"
        elif port_custom and protocol_custom:
            command_filter = (
                f"{port_custom} {logic_operator_proto_red_proto} {protocol_custom}"
            )
        elif ips_custom:
            command_filter = f"{ips_custom}"
        elif port_custom:
            command_filter = f"{port_custom}"
        elif protocol_custom:
            command_filter = f"{protocol_custom}"

        fecha_creacion = datetime.now()
        filtro = FilterPacket(
            0,
            name_filter,
            type_filter,
            command_filter,
            plataforms,
            fecha_creacion,
            current_user.id,
        )
        modelFilterPacket.insertFilter(filtro)

        return "Filtro guardado correctamente"
    except Exception as e:
        return f"Error al guardar el filtro: {str(e)}"


def save_report(nombre_reporte, filtro_monitoreo, table_data):
    try:
        df = pd.DataFrame(table_data)

        # Crear el archivo Excel en memoria
        excel_file = BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)

        # Leer los bytes del archivo Excel
        excel = excel_file.read()
        excel_base64 = base64.b64encode(excel).decode("utf-8")

        # Cerrar el archivo Excel en memoria
        excel_file.close()

        fecha_creacion = datetime.now()
        reporte = Monitoreo(
            0,
            nombre_reporte,
            excel_base64,
            fecha_creacion,
            filtro_monitoreo,
            current_user.id,
        )
        modelPaquetes.insertPacket(reporte)

        return "Reporte guardado correctamente"
    except Exception as e:
        return f"Error al guardar el reporte: {str(e)}"


def load_filter_data():
    try:
        filtros = modelFilterPacket.getFilters()

        filtros_formateados = []

        palabras_clave = ["http", "https", "smtp", "ssh", "ftp", "telnet"]

        for filtro in filtros:
            fecha = filtro[5].strftime("%d-%m-%Y")
            filtro_creado = filtro[3]
            contenido = filtro[4]

            ip = ""
            puerto = ""
            protocolo = ""
            protocolo_red = ""

            partes_con_palabras_clave = []
            otras_partes = []

            conjuntos_parentesis = re.findall(r"\((.*?)\)", filtro_creado)

            if contenido:
                # Crear un diccionario con los valores formateados
                filtro_formateado = {
                    "id": filtro[0],
                    "nombre_filtro": filtro[1].title(),
                    "tipo_filtro": filtro[2],
                    "filtro": filtro[3],
                    "fecha_creacion": fecha,
                    "ip": ip,
                    "puerto": puerto,
                    "protocolo_red": protocolo_red,
                    "protocolo": protocolo,
                    "consumos": contenido.title().replace("_", " ").replace("-", " "),
                }
            else:
                for conjunto in conjuntos_parentesis:
                    if "host" in conjunto.lower():
                        ip = conjunto
                    elif "port" in conjunto.lower():
                        # puerto = conjunto
                        partes_puerto = re.split(r"\b(and|or)\b", conjunto.lower())

                        for i, parte in enumerate(partes_puerto):
                            # Verificar si es una parte válida (no operador)
                            if parte not in ["and", "or"]:
                                # Verificar si la parte contiene palabras clave
                                if any(palabra in parte for palabra in palabras_clave):
                                    # Agregar la parte a la lista y verificar la siguiente posición
                                    partes_con_palabras_clave.append(parte.strip())
                                    if i + 1 < len(partes_puerto) and partes_puerto[
                                        i + 1
                                    ] in ["and", "or"]:
                                        partes_con_palabras_clave[-1] += (
                                            " " + partes_puerto[i + 1]
                                        )
                                else:
                                    # Agregar la parte a la lista y verificar la siguiente posición
                                    otras_partes.append(parte.strip())
                                    if i + 1 < len(partes_puerto) and partes_puerto[
                                        i + 1
                                    ] in ["and", "or"]:
                                        otras_partes[-1] += " " + partes_puerto[i + 1]

                        # Unir las partes que contienen palabras clave en una sola variable
                        protocolo_red = " ".join(partes_con_palabras_clave)

                        # Unir las otras partes en otra variable
                        puerto = " ".join(otras_partes)

                    else:
                        protocolo = conjunto

                # Crear un diccionario con los valores formateados
                filtro_formateado = {
                    "id": filtro[0],
                    "nombre_filtro": filtro[1].title(),
                    "tipo_filtro": filtro[2],
                    "filtro": filtro[3],
                    "fecha_creacion": fecha,
                    "ip": ip,
                    "puerto": puerto,
                    "protocolo_red": protocolo_red,
                    "protocolo": protocolo,
                    "consumos": "",
                }

            # Agregar el filtro formateado a la lista
            filtros_formateados.append(filtro_formateado)

        return filtros_formateados
    except Exception as e:
        return f"Error al cargar el reporte: {str(e)}"


def load_report():
    try:
        registros = modelPaquetes.getPackets()

        registros_modificados = []
        for registro in registros:
            registro_modificado = list(registro)
            registro_modificado[2] = registro_modificado[2].strftime("%d-%m-%Y")
            registros_modificados.append(tuple(registro_modificado))

        return registros_modificados
    except Exception as e:
        return f"Error al cargar el reporte: {str(e)}"


def load_reportData(id_report):
    try:
        registro_data = modelPaquetes.getPacketById(id_report)
        excel_data_base64 = registro_data[0]
        excel_data_bytes = base64.b64decode(excel_data_base64)

        # Crear un DataFrame de Pandas desde el archivo Excel
        df = pd.read_excel(BytesIO(excel_data_bytes))

        # Convertir el DataFrame a JSON
        json_data = df.to_json(orient="records")

        return {"data": json_data}
    except Exception as e:
        return f"Error al mostrar el reporte: {str(e)}"


def delete_report(id_reporte):
    try:
        print(id_reporte)
        modelPaquetes.deletePacket(id_reporte)

        return "Reporte Eliminado"
    except subprocess.CalledProcessError as e:
        # Maneja cualquier error que pueda ocurrir durante la ejecución del comando
        print(f"Error al obtener el número de la regla: {e}")
        return None


def delete_filter(id_filter):
    try:
        modelFilterPacket.deleteFilter(id_filter)

        return "Reporte Eliminado"
    except Exception as e:
        return f"Error al obtener el número de la regla: {str(e)}"
