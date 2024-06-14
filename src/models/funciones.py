import base64
from datetime import datetime
from io import BytesIO

import shlex
from flask import Response, flash, jsonify
from flask_login import current_user, login_user
import pandas as pd

import re

import subprocess

# Models
from models.modelUser import modelUser
from models.modelFirewall import modelFirewall
from models.modelFirewallDetail import modelFirewallDetail
from models.modelMonitoreo import modelPaquetes
from models.modelFilterPacket import modelFilterPacket
from models.modelCommunity import modelCommunity
from models.modelAutomation import modelAutomation

# Entities
from models.entities.user import User
from models.entities.firewall import Firewall
from models.entities.firewallDetail import FirewallDetail
from models.entities.monitoreo import Monitoreo
from models.entities.filterPacket import FilterPacket
from models.entities.community import Community
from models.entities.automationFirewall import Automation


def validar_ingreso(username, password_hash):
    try:
        if "firewall" in username:
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
        else:
            flash("Usuario no permitido")
        return False
    except Exception as e:
        return str(e)


def is_valid_ip(ip):
    # Expresión regular para verificar el formato de la IP
    ip_regex = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"

    return re.match(ip_regex, ip) is not None


def is_valid_mac(mac):
    # Expresión regular para verificar el formato de la MAC
    mac_regex = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"

    return re.match(mac_regex, mac) is not None


def obtener_reglas_ufw():
    try:
        reglas_in = []
        reglas_out = []
        reglas_default = []

        domains_duplicated = set()

        rule_db = modelFirewall.getRules()

        if rule_db:
            for rule_tuple in rule_db:
                id_regla = rule_tuple[0]
                assigned_name = rule_tuple[1].replace("_", " ").replace("-", " ")
                status = rule_tuple[4]
                created_date = rule_tuple[3].strftime("%Y-%m-%d")
                tipo_regla = rule_tuple[2]

                detail_domain_rules = modelFirewallDetail.getRulesDetailsById(id_regla)

                domains = []

                for detail_domain in detail_domain_rules:
                    rule_data = ""
                    ip = ""
                    port = ""

                    detail_status = detail_domain[2]
                    if tipo_regla in ["contenido", "dominio"] and detail_status == 1:
                        rule_detail_parts = detail_domain[1].split(
                            " -m comment --comment "
                        )
                        rule_detail_command = rule_detail_parts[0].split()
                        rule_detail_domain = rule_detail_parts[1].replace("'", "")

                        if rule_detail_domain not in domains_duplicated:
                            count_hyphens = rule_detail_domain.count("-")

                            domain = rule_detail_domain.split("-", count_hyphens)[
                                count_hyphens
                            ].strip()

                            domains.append(domain)
                            domains_duplicated.add(rule_detail_domain)

                        rule_data = ", ".join(domains)

                    else:
                        rule_detail_parts = detail_domain[1].split(" comment ")
                        rule_detail_command = (
                            rule_detail_parts[0].replace("/", " ").split()
                        )
                        name_rule = rule_detail_parts[1].replace("'", "")

                        for part in rule_detail_command:
                            if is_valid_ip(part) or is_valid_mac(part):
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
                            "nombre": name_rule,
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
                        "dominio": "No hay dominios habilitados"
                        if not rule_data
                        else rule_data,
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


def obtener_reglas_ufw_contenido():
    try:
        reglas_contenido = {}
        reglas_contenido_sorted = {}

        domains_duplicated = []

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
                    rule_name = rule_parts[1]

                    if rule_name not in domains_duplicated:
                        domain = rule_name.split("-", 2)[2].strip().replace("'", "")

                        if "ACCEPT" in rule_command:
                            permiso = "PERMITIDO"
                        elif "REJECT" in rule_command:
                            permiso = "DENEGADO"

                        protocolo = (
                            "TCP"
                            if "tcp" in rule_command
                            else "UDP"
                            if "udp" in rule_command
                            else "TCP/UDP"
                        )
                        entry = (
                            "ENTRADA"
                            if "INPUT" in rule_command
                            else "SALIDA"
                            if "OUTPUT" in rule_command
                            else "ENTRADA"
                        )

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
                            reglas_contenido[(assigned_name, id_regla, name_rule)] = [
                                regla
                            ]
                        else:
                            reglas_contenido[
                                (assigned_name, id_regla, name_rule)
                            ].append(regla)

                        domains_duplicated.append(rule_name)
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
        command = "/sbin/arp-scan -l"
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        stdout, _ = process.communicate()

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


def delete_rule(regla_content_id, id_regla):
    try:
        if regla_content_id:
            rule_details = {}
            rule_details_copy = {}

            rule_detail = modelFirewallDetail.getDetailById(regla_content_id)
            rule_string = rule_detail[1]
            estado_detail = rule_detail[2]
            id_regla_detalle = rule_detail[3]

            detail_rules = modelFirewallDetail.getRulesDetailsById(id_regla_detalle)

            for detail_rule in detail_rules:
                rule_detail_id, rule_string_items, _ = detail_rule

                rule_details[rule_detail_id] = rule_string_items

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
                        "/sbin/iptables",
                        "-L",
                        direccion,
                        "--line-numbers",
                        "-n",
                    ]
                )

                iptables_rules_matched(salida_iptables, rule_detail_name, direccion)

                if "REJECT" in rule_string:
                    remove_domain_from_hosts(rule_detail_name)

            rule_details_copy = rule_details.copy()

            for rule_detail_id, rule_string_items in rule_details_copy.items():
                if rule_detail_name not in rule_string_items:
                    del rule_details[rule_detail_id]

            for rule_detail_id, _ in rule_details.items():
                modelFirewallDetail.deleteDetailById(rule_detail_id)

        else:
            rule_db_filter = modelFirewall.getRuleById(id_regla)

            rule_name = rule_db_filter[2]
            tipo_regla = rule_db_filter[3]

            numero_data = int(rule_db_filter[5])

            detail_rules = modelFirewallDetail.getRulesDetailsById(id_regla)

            if numero_data == 1:
                for detail_rule in detail_rules:
                    rule_string = detail_rule[1]

                    if (
                        tipo_regla in ["contenido", "dominio"]
                        or "iptables" in rule_string
                    ):
                        if "INPUT" in rule_string:
                            direccion = "INPUT"
                        elif "OUTPUT" in rule_string:
                            direccion = "OUTPUT"

                    else:
                        rule_delete = (
                            f"{rule_string.replace('/sbin/ufw ', '/sbin/ufw delete ')}"
                        )

                        print(rule_delete)

                        subprocess.run(
                            shlex.split(f"{rule_delete}"),
                            input="y\n",
                            text=True,
                            capture_output=True,
                        )

                if tipo_regla in ["contenido", "dominio"] or "iptables" in rule_string:
                    salida_iptables = subprocess.check_output(
                        [
                            "/sbin/iptables",
                            "-L",
                            direccion,
                            "--line-numbers",
                            "-n",
                        ]
                    )

                    iptables_rules_matched(salida_iptables, rule_name, direccion)

                    if (
                        tipo_regla in ["contenido", "dominio"]
                        and "REJECT" in rule_string
                    ):
                        remove_domain_from_hosts(rule_name)

            modelFirewallDetail.deleteRuleDetail(id_regla)
            modelFirewall.deleteRule(id_regla)

        save_iptables_rules()

        return jsonify({"message": "¡Regla Eliminada Correctamente!"})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Error al obtener el número de la regla: {e}"})


def deactivate_activate_rule(id_regla, regla_content_id):
    try:
        rule_details = {}
        rule_details_copy = {}
        domains_duplicated = []
        dynamic_domains = []

        message = ""

        if regla_content_id:
            rule_detail = modelFirewallDetail.getDetailById(regla_content_id)
            rule_string = rule_detail[1]
            estado_detail = rule_detail[2]
            id_regla_detalle = rule_detail[3]

            detail_rules = modelFirewallDetail.getRulesDetailsById(id_regla_detalle)

            for detail_rule in detail_rules:
                rule_detail_id, rule_string_items, _ = detail_rule

                rule_details[rule_detail_id] = rule_string_items

            rule_detail_name = rule_string.split(" -m comment --comment ")[1].replace(
                "'", ""
            )

            rule_details_copy = rule_details.copy()

            for rule_detail_id, rule_string_items in rule_details_copy.items():
                if rule_detail_name not in rule_string_items:
                    del rule_details[rule_detail_id]

            if estado_detail == 1:
                if "INPUT" in rule_string:
                    direccion = "INPUT"
                elif "OUTPUT" in rule_string:
                    direccion = "OUTPUT"

                salida_iptables = subprocess.check_output(
                    [
                        "/sbin/iptables",
                        "-L",
                        direccion,
                        "--line-numbers",
                        "-n",
                    ]
                )

                iptables_rules_matched(salida_iptables, rule_detail_name, direccion)

                if "REJECT" in rule_string:
                    remove_domain_from_hosts(rule_detail_name)

                for rule_detail_id, _ in rule_details.items():
                    modelFirewallDetail.updateDetail(0, rule_detail_id)

                all_rules_disabled = True

                detail_rules_status = modelFirewallDetail.getRulesDetailsById(
                    id_regla_detalle
                )

                for detail_rule in detail_rules_status:
                    _, _, status_rule = detail_rule

                    if status_rule == 1:
                        all_rules_disabled = False

                if all_rules_disabled:
                    modelFirewall.updateRule(0, id_regla_detalle)

                message = "¡Regla Desactivada Correctamente!"

            elif estado_detail == 0:
                domain_dynamic = rule_detail_name.split("-", 2)[2].strip()

                if domain_dynamic in plataformas_dinamicas_dominio:
                    rule_name_content = " - ".join(
                        [part.strip() for part in rule_detail_name.split("-", 2)[:2]]
                    )

                    entry = "OUTPUT" if "OUTPUT" in rule_string_items else "INPUT"
                    action_rule = (
                        "REJECT" if "REJECT" in rule_string_items else "ACCEPT"
                    )

                    for rule_detail_id, _ in rule_details.items():
                        modelFirewallDetail.deleteDetailById(rule_detail_id)

                    allow_connections_detail(
                        id_regla_detalle,
                        rule_name_content,
                        action_rule,
                        entry,
                        domain_dynamic,
                    )

                else:
                    for rule_detail_id, rule_string_items in rule_details.items():
                        rule_detail_domain = rule_string_items.split(
                            " -m comment --comment "
                        )[1].replace("'", "")

                        rule = f"{rule_string_items}"
                        subprocess.run(shlex.split(f"{rule}"))

                        modelFirewallDetail.updateDetail(1, rule_detail_id)

                        if "REJECT" in rule_string_items:
                            if rule_detail_domain not in domains_duplicated:
                                count_hyphens = rule_detail_domain.count("-")

                                domain = rule_detail_domain.split("-", count_hyphens)[
                                    count_hyphens
                                ].strip()

                                add_domain_to_hosts(domain, rule_detail_domain)
                                domains_duplicated.append(rule_detail_domain)

                detail_rules_status = modelFirewallDetail.getRulesDetailsById(
                    id_regla_detalle
                )

                all_rules_disabled = all(
                    status_rule == 1 for _, _, status_rule in detail_rules_status
                )

                if not all_rules_disabled:
                    modelFirewall.updateRule(1, id_regla_detalle)

                message = "¡Regla Activada Correctamente!"

            save_iptables_rules()

            return jsonify({"message": message})

        elif id_regla:
            rule_db_filter = modelFirewall.getRuleById(id_regla)

            rule_name = rule_db_filter[2]
            numero_data = int(rule_db_filter[5])
            tipo_regla = rule_db_filter[3]

            detail_rules = modelFirewallDetail.getRulesDetailsById(id_regla)
            for detail_rule in detail_rules:
                rule_detail_id, rule_string, _ = detail_rule

                if numero_data == 1:
                    if (
                        tipo_regla in ["contenido", "dominio"]
                        or "iptables" in rule_string
                    ):
                        if "INPUT" in rule_string:
                            direccion = "INPUT"
                        elif "OUTPUT" in rule_string:
                            direccion = "OUTPUT"

                    else:
                        rule_delete = (
                            f"{rule_string.replace('/sbin/ufw ', '/sbin/ufw delete ')}"
                        )

                        print(rule_delete)

                        subprocess.run(
                            shlex.split(f"{rule_delete}"),
                            input="y\n",
                            text=True,
                            capture_output=True,
                        )

                    modelFirewallDetail.updateDetail(0, rule_detail_id)

                elif numero_data == 0:
                    if (
                        tipo_regla in ["contenido", "dominio"]
                        and "REJECT" in rule_string
                    ):
                        rule_detail_parts = rule_string.split(" -m comment --comment ")
                        rule_detail_domain = rule_detail_parts[1].replace("'", "")

                        count_hyphens = rule_detail_domain.count("-")

                        domain = rule_detail_domain.split("-", count_hyphens)[
                            count_hyphens
                        ].strip()

                        if domain in plataformas_dinamicas_dominio:
                            if rule_detail_domain not in domains_duplicated:
                                dynamic_domains.append(
                                    (rule_detail_id, domain, rule_string, tipo_regla)
                                )
                                domains_duplicated.append(rule_detail_domain)
                            modelFirewallDetail.deleteDetailById(rule_detail_id)
                            continue
                        else:
                            rule = f"{rule_string}"
                            subprocess.run(shlex.split(f"{rule}"))

                        if rule_detail_domain not in domains_duplicated:
                            add_domain_to_hosts(domain, rule_detail_domain)
                            domains_duplicated.append(rule_detail_domain)

                    else:
                        rule = f"{rule_string}"
                        subprocess.run(shlex.split(f"{rule}"))

                    modelFirewallDetail.updateDetail(1, rule_detail_id)

            if dynamic_domains:
                for dynamic_domain in dynamic_domains:
                    rule_detail_id, domain, rule_string, tipo_regla = dynamic_domain

                    rule_detail_name = rule_string.split(" -m comment --comment ")[
                        1
                    ].replace("'", "")

                    count_hyphens = rule_detail_domain.count("-")
                    domain_dynamic = rule_detail_domain.split("-", count_hyphens)[
                        count_hyphens
                    ].strip()

                    rule_name_content = " - ".join(
                        [
                            part.strip()
                            for part in rule_detail_name.split("-", count_hyphens)[
                                :count_hyphens
                            ]
                        ]
                    )

                    entry = "OUTPUT" if "OUTPUT" in rule_string else "INPUT"
                    action_rule = "REJECT" if "REJECT" in rule_string else "ACCEPT"

                    allow_connections_detail(
                        id_regla,
                        rule_name_content,
                        action_rule,
                        entry,
                        domain_dynamic,
                    )

            if numero_data == 1:
                if tipo_regla in ["contenido", "dominio"] or "iptables" in rule_string:
                    salida_iptables = subprocess.check_output(
                        ["/sbin/iptables", "-L", direccion, "--line-numbers", "-n"]
                    )
                    iptables_rules_matched(salida_iptables, rule_name, direccion)
                    if (
                        tipo_regla in ["contenido", "dominio"]
                        and "REJECT" in rule_string
                    ):
                        remove_domain_from_hosts(rule_name)

                modelFirewall.updateRule(0, id_regla)
                message = "¡Regla Desactivada Correctamente!"

            elif numero_data == 0:
                modelFirewall.updateRule(1, id_regla)
                message = "¡Regla Activada Correctamente!"

            save_iptables_rules()

            return jsonify({"message": message})

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Error al obtener el número de la regla: {e}"})


def iptables_rules_matched(salida_iptables, name_iptable, direccion):
    reglas = salida_iptables.decode("utf-8").splitlines()
    id_iptable_delete = None

    consulta_formateada = "\n".join(reglas[2:])

    for line in consulta_formateada.splitlines():
        id_iptable_rule = line.split()[0]
        if name_iptable in line:
            if id_iptable_delete is None:
                id_iptable_delete = id_iptable_rule

            rule_delete = f"/sbin/iptables -D {direccion} {id_iptable_delete}"

            subprocess.run(
                shlex.split(f"{rule_delete}"),
            )

    return "¡Regla Eliminada Correctamente!"


def save_iptables_rules():
    with open("/home/firewall/iptables/rules.v4", "w") as save:
        subprocess.run(["/sbin/iptables-save"], stdout=save)


def execute_command(command):
    # Ejecutar el comando y capturar la salida
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout


# Este diccionario es el que va a devolver para la vista
plataformas_unificadas = {
    "redes_sociales": [
        "www.facebook.com",
        "twitter.com",
        "www.instagram.com",
        "ec.linkedin.com",
        "www.linkedin.com",
        "www.pinterest.com",
        "snapchat.com",
        "x.com",
        "www.tiktok.com",
    ],
    "videojuegos": [
        "store.steampowered.com",
        "store.epicgames.com",
        "origin.com",
        "uplay.com",
        "gog.com",
        "ubisoftconnect.com",
        "www.gog.com",
        "www.ea.com",
    ],
    "musica": ["open.spotify.com", "pandora.com"],
    "streaming": [
        "www.hulu.com",
        "www.primevideo.com",
        "www.disneyplus.com",
        "www.hbo.com",
        "www.max.com",
        "www.netflix.com",
    ],
    "lectura": ["www.scribd.com", "www.wattpad.com", "www.goodreads.com"],
    "video": ["vimeo.com", "www.dailymotion.com", "www.youtube.com", "www.twitch.tv"],
    "mensajeria": [
        "web.whatsapp.com",
        "facebook.com",
        "web.telegram.org",
        "discord.com",
    ],
    "podcast": ["open.spotify.com", "www.stitcher.com", "www.podbean.com"],
    "mailing": [
        "mail.google.com",
        "mail.aol.com",
        "outlook.live.com",
        "mail.yahoo.com",
        "www.aol.com",
        "proton.me",
    ],
    "imagenes": ["www.flickr.com", "unsplash.com", "imgur.com"],
    "ecommerce": [
        "www.amazon.com",
        "www.ebay.com",
        "www.walmart.com",
        "www.target.com",
        "www.etsy.com",
    ],
    "blogging": ["wordpress.com", "www.blogger.com", "www.tumblr.com", "medium.com"],
    "pagos": ["www.paypal.com", "squareup.com", "www.authorize.net", "stripe.com"],
    "apuestas": [
        "www.bet365.com",
        "www.bet365.es",
        "sports.bwin.com",
        "www.888sport.com",
        "www.williamhill.com",
        "www.betfair.com",
        "www.unibet.com",
        "sports.ladbrokes.com",
        "sports.coral.co.uk",
        "www.unibet.co.uk",
    ],
    "educacion": [
        "www.coursera.org",
        "www.udemy.com",
        "www.khanacademy.org",
        "www.edx.org",
        "www.udacity.com",
    ],
    "crm": [
        "www.zoho.com",
        "www.hubspot.com",
        "business.adobe.com",
        "www.salesforce.com",
        "pardot.com",
    ],
    "redes_profesionales": ["www.linkedin.com", "ec.indeed.com", "www.glassdoor.com"],
    "trabajo_colaborativo": ["www.dropbox.com"],
    "videoconferencias": ["zoom.us", "teams.microsoft.com"],
}


def get_plataforms():
    plataforms_key = list(plataformas_unificadas.keys())
    plataforms = [
        key.replace("_", " ").title() for key in plataformas_unificadas.keys()
    ]

    return plataforms, plataforms_key


def get_plataforms_domain(key):
    domains = plataformas_unificadas[key]

    return domains


# Plataformas con ips estaticas
plataformas = {
    "redes_sociales": [
        "www.facebook.com",
        "twitter.com",
        "www.instagram.com",
        "ec.linkedin.com",
        "www.linkedin.com",
        "www.pinterest.com",
        "snapchat.com",
        "x.com",
    ],
    "videojuegos": [
        "store.steampowered.com",
        "store.epicgames.com",
        "origin.com",
        "uplay.com",
        "gog.com",
        "ubisoftconnect.com",
        "www.gog.com",
        "www.ea.com",
    ],
    "musica": [
        "open.spotify.com",
        "pandora.com",
    ],
    "streaming": [
        "www.hulu.com",
        "www.primevideo.com",
        "www.disneyplus.com",
        "www.hbo.com",
        "www.max.com",
    ],
    "lectura": [
        "www.scribd.com",
        "www.wattpad.com",
        "www.goodreads.com",
    ],
    "video": ["vimeo.com", "www.dailymotion.com"],
    "mensajeria": [
        "web.whatsapp.com",
        "facebook.com",
        "web.telegram.org",
        # "slack.com",
        "discord.com",
    ],
    "podcast": [
        "open.spotify.com",
        "www.stitcher.com",
        "www.podbean.com",
    ],
    "mailing": [
        "mail.google.com",
        "mail.aol.com",
        "outlook.live.com",
        "mail.yahoo.com",
        "www.aol.com",
        "proton.me",
    ],
    "imagenes": ["www.flickr.com", "unsplash.com", "imgur.com"],
    "ecommerce": [
        "www.amazon.com",
        "www.ebay.com",
        "www.walmart.com",
        "www.target.com",
        "www.etsy.com",
    ],
    "blogging": [
        "wordpress.com",
        "www.blogger.com",
        "www.tumblr.com",
        "medium.com",
    ],
    "pagos": [
        "www.paypal.com",
        "squareup.com",
        "www.authorize.net",
    ],
    "apuestas": [
        "www.bet365.com",
        "www.bet365.es",
        "sports.bwin.com",
        "www.888sport.com",
        "www.williamhill.com",
        "www.betfair.com",
        "www.unibet.com",
        "sports.ladbrokes.com",
        "sports.coral.co.uk",
        "www.unibet.co.uk",
    ],
    "educacion": [
        "www.coursera.org",
        "www.udemy.com",
        "www.khanacademy.org",
        "www.edx.org",
        "www.udacity.com",
    ],
    "crm": [
        "www.zoho.com",
        "www.hubspot.com",
        "business.adobe.com",
    ],
    "redes_profesionales": ["www.linkedin.com", "ec.indeed.com", "www.glassdoor.com"],
    "trabajo_colaborativo": ["www.dropbox.com"],
    "videoconferencias": ["zoom.us", "teams.microsoft.com"],
}

# Plataformas con ips dinamicas
plataformas_dinamicas = {
    "redes_sociales": [
        "www.tiktok.com",
    ],
    "videojuegos": [],
    "musica": [],
    "streaming": [
        "www.netflix.com",
    ],
    "lectura": [],
    "educacion": [],
    "podcast": [],
    "mensajeria": [],
    "mailing": [],
    "blogging": [],
    "imagenes": [],
    "ecommerce": [],
    "pagos": [
        "stripe.com",
    ],
    "crm": [
        "www.salesforce.com",
        "pardot.com",
    ],
    "redes_profesionales": [],
    "trabajo_colaborativo": [],
    "videoconferencias": [],
    "apuestas": [],
    "video": ["www.youtube.com", "www.twitch.tv"],
}

plataformas_dinamicas_dominio = [
    "www.tiktok.com",
    "www.youtube.com",
    "www.twitch.tv",
    "www.netflix.com",
    "www.apple.com",
    "stripe.com",
    "pardot.com",
    "www.salesforce.com",
]


def add_domain_to_hosts(domain, name_domain):
    with open("/etc/hosts", "a") as hosts_file:
        hosts_file.write(f"127.0.0.1\t{domain}\t# {name_domain}\n")


def remove_domain_from_hosts(name_domain):
    with open("/etc/hosts", "r") as hosts_file:
        lines = hosts_file.readlines()

    with open("/etc/hosts", "w") as hosts_file:
        for line in lines:
            if name_domain not in line:
                hosts_file.write(line)


def allow_connections(
    action_rule,
    rule_type,
    ip_addr,
    local_red,
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
        protocol = (
            ["tcp", "udp"]
            if protocol == "tcp/udp" and local_red
            else protocol
            if protocol != "tcp/udp"
            else ""
        )

        ip_dest = "" if entry == "out" else "any"

        if entry == "in":
            direction = "from"
        elif entry == "out":
            direction = "to"

        rule = f"/sbin/ufw {action_rule}"
        fecha_creacion = datetime.now()

        rulesTypeContent = []
        rules_protocols = []

        if rule_type in ("dominio", "contenido") or local_red:
            action_rule = "ACCEPT" if action_rule == "allow" else "REJECT"
            entry = "INPUT" if entry == "in" else "OUTPUT"
            direction = "-s" if entry == "INPUT" else "-d"

        if content_tp:
            reglas_contenido = modelFirewall.getRulesContent()

            for platform in content_tp:
                plataforma_contenido = platform.replace("_", " ").lower().title()

                if any(
                    plataforma_contenido == rule_tuple[1].split(" - ")[1].strip()
                    for rule_tuple in reglas_contenido
                ):
                    return jsonify(
                        {"error": "Ya existe una regla con ese tipo de contenido"}
                    )

                if platform in plataformas:
                    platform_name = platform.replace("_", " ").title()
                    rules_content = []
                    comment_content = f"{comment} - {platform_name}"

                    domains = plataformas[platform] + plataformas_dinamicas[platform]

                    for domain_platform in domains:
                        ip_domain = (
                            verify_domain_dynamic(domain_platform)
                            if domain_platform in plataformas_dinamicas[platform]
                            else domain_platform
                        )

                        comment_with_domain = f"{comment_content} - {domain_platform}"

                        if isinstance(ip_domain, list):
                            for ip in ip_domain:
                                rule = f"/sbin/iptables -I {entry} 1 {direction} {ip} -j {action_rule} -m comment --comment '{comment_content} - {domain_platform}'"
                                rules_content.append(rule)
                                subprocess.run(shlex.split(rule))

                        elif isinstance(ip_domain, str):
                            rule = f"/sbin/iptables -I {entry} 1 {direction} {ip_domain} -j {action_rule} -m comment --comment '{comment_content} - {domain_platform}'"
                            rules_content.append(rule)
                            subprocess.run(shlex.split(rule))

                        if action_rule == "REJECT":
                            add_domain_to_hosts(domain_platform, comment_with_domain)

                    rulesTypeContent.append((rules_content, comment_content))
                else:
                    print(f"Invalid platform: {platform_name}")

        elif domain:
            rules_domain_dynamic = []

            comment_domain = f"{comment} - {domain}"

            if domain in plataformas_dinamicas_dominio:
                ip_domain = verify_domain_dynamic(domain)

                if isinstance(ip_domain, list):
                    rules_domain_dynamic = [
                        f"/sbin/iptables -I {entry} 1 {direction} {ip} -j {action_rule} -m comment --comment '{comment_domain}'"
                        for ip in ip_domain
                    ]
                elif isinstance(ip_domain, str):
                    rules_domain_dynamic = [
                        f"/sbin/iptables -I {entry} 1 {direction} {ip_domain} -j {action_rule} -m comment --comment '{comment_domain}'"
                    ]
            else:
                rules_domain_dynamic = [
                    f"/sbin/iptables -I {entry} 1 {direction} {domain} -j {action_rule} -m comment --comment '{comment_domain}'"
                ]

            for rule in rules_domain_dynamic:
                subprocess.run(shlex.split(rule))

            if action_rule == "REJECT":
                add_domain_to_hosts(domain, comment_domain)

        elif port and (ip_addr or local_red):
            if ip_addr:
                if ip_addr and netmask:
                    ip_addr += f"/{netmask}"
                if ip_dest and dest_netmask:
                    ip_dest += f"/{dest_netmask}"

                elif entry and direction and ip_addr and ip_dest and port and protocol:
                    rule += f" {entry} {direction} {ip_addr} to {ip_dest} port {port} proto {protocol} comment '{comment}'"

                elif entry and direction and ip_addr and port and protocol:
                    rule += f" {entry} {direction} {ip_addr} port {port} proto {protocol} comment '{comment}'"

                elif entry and direction and ip_addr and ip_dest and port:
                    rule += f" {entry} {direction} {ip_addr} to {ip_dest} port {port} comment '{comment}'"

                elif entry and direction and ip_addr and ip_dest and port:
                    rule += f" {entry} {direction} {ip_addr} to {ip_dest} {port} comment '{comment}'"

                elif entry and direction and ip_dest and port and protocol:
                    rule += f" {entry} {direction} any to {ip_dest} port {port} proto {protocol} comment '{comment}'"

                elif entry and direction and ip_addr and port and protocol:
                    rule += f" {entry} {direction} {ip_addr} port {port} proto {protocol} comment '{comment}'"

                elif entry and direction and ip_addr and port:
                    rule += f" {entry} {direction} {ip_addr} port {port} comment '{comment}'"

                elif entry and direction and ip_dest and port:
                    rule += f" {entry} {direction} any to {ip_dest} port {port} comment '{comment}'"

            else:
                if isinstance(protocol, list):
                    for protocol_option in protocol:
                        rule = f"/sbin/iptables -I {entry} -p {protocol_option} --dport {port} -m mac --mac-source {local_red} -j {action_rule} -m comment --comment '{comment}'"
                        rules_protocols.append(rule)

                else:
                    rule = f"/sbin/iptables -I {entry} -p {protocol} --dport {port} -m mac --mac-source {local_red} -j {action_rule} -m comment --comment '{comment}'"

            if rules_protocols:
                for rule in rules_protocols:
                    subprocess.run(shlex.split(f"{rule}"))

            else:
                subprocess.run(shlex.split(f"{rule}"))

        # IPs
        elif ip_addr or local_red:
            if ip_addr:
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
                    rule += f" {entry} {direction} {ip_addr} to {ip_dest} comment '{comment}'"

                elif entry and direction and ip_addr:
                    rule += f" {entry} {direction} {ip_addr} comment '{comment}'"

                elif entry and direction and ip_dest:
                    rule += f" {entry} {direction} any to {ip_dest} comment '{comment}'"

            else:
                if local_red and protocol:
                    if isinstance(protocol, list):
                        for protocol_option in protocol:
                            rule = f"/sbin/iptables -I {entry} -p {protocol_option} -m mac --mac-source {local_red} -j {action_rule} -m comment --comment '{comment}'"
                            rules_protocols.append(rule)

                    else:
                        rule = f"/sbin/iptables -I {entry} -p {protocol} -m mac --mac-source {local_red} -j {action_rule} -m comment --comment '{comment}'"

                else:
                    rule = f"/sbin/iptables -I {entry} -m mac --mac-source {local_red} -j {action_rule} -m comment --comment '{comment}'"

            if rules_protocols:
                for rule in rules_protocols:
                    subprocess.run(shlex.split(f"{rule}"))

            else:
                subprocess.run(shlex.split(f"{rule}"))

        # Port
        elif port:
            if entry == "in" and port and protocol:
                rule += f" {entry} {port}/{protocol} comment '{comment}'"

            elif entry == "in" and port:
                rule += f" {entry} {port} comment '{comment}'"

            elif entry and direction and port and protocol:
                rule += f" {entry} {direction} any port {port} proto {protocol} comment '{comment}'"

            elif entry and direction and port:
                rule += f" {entry} {direction} any port {port} comment '{comment}'"

            subprocess.run(shlex.split(f"{rule}"))

        if rulesTypeContent:
            for rulesContentPlatform in rulesTypeContent:
                firewall = Firewall(
                    0,
                    rulesContentPlatform[1],
                    rule_type,
                    fecha_creacion,
                    1,
                    current_user.id,
                )

                firewall = modelFirewall.insertRule(firewall)
                id_rule = firewall.id

                # Iteramos sobre las reglas de la plataforma actual
                for rule in rulesContentPlatform[0]:
                    firewallDetail = FirewallDetail(0, id_rule, rule, 1)
                    modelFirewallDetail.insertRuleDetail(firewallDetail)

        elif domain:
            firewall = Firewall(
                0,
                comment_domain,
                rule_type,
                fecha_creacion,
                1,
                current_user.id,
            )
            firewall = modelFirewall.insertRule(firewall)
            id_rule = firewall.id

            if rules_domain_dynamic:
                for domain_rule_ip in rules_domain_dynamic:
                    firewallDetail = FirewallDetail(0, id_rule, domain_rule_ip, 1)
                    modelFirewallDetail.insertRuleDetail(firewallDetail)
            else:
                firewallDetail = FirewallDetail(0, id_rule, rule, 1)
                modelFirewallDetail.insertRuleDetail(firewallDetail)

        else:
            firewall = Firewall(
                0,
                comment,
                rule_type,
                fecha_creacion,
                1,
                current_user.id,
            )
            firewall = modelFirewall.insertRule(firewall)
            id_rule = firewall.id

            firewallDetail = FirewallDetail(0, id_rule, rule, 1)
            modelFirewallDetail.insertRuleDetail(firewallDetail)

        save_iptables_rules()

        return jsonify({"message": "¡Regla creada correctamente!"})
    except subprocess.CalledProcessError:
        return jsonify({"error": "Error al permitir el puerto."})


def create_community(
    community_name,
    community_type,
    local_ip,
    initial_ip,
    final_ip,
):
    try:
        fecha_creacion = datetime.now()

        if local_ip:
            local_ip = ",".join(local_ip)
            rango = local_ip
        else:
            rango = f"{initial_ip} - {final_ip}"

        community = Community(
            0,
            community_name,
            community_type,
            rango,
            fecha_creacion,
            1,
            current_user.id,
        )
        community = modelCommunity.insertCommunity(community)

        return jsonify({"message": "¡Comunidad creada correctamente!"})
    except subprocess.CalledProcessError:
        return jsonify({"error": "Error al permitir el puerto."})


def create_automation(
    automation_name,
    automation_type,
    automation_action,
    domain,
    content_type,
    domain_plataform,
    comunidad_id,
    horario,
):
    try:
        fecha_creacion = datetime.now()

        restriccion = content_type

        with open("/etc/squid/squid-restriction/blacklist", "a") as save:
            for domain_content in domain_plataform:
                save.write(domain_content + "\n")

        dias_mapeo = {
            "Lunes": "M",
            "Martes": "T",
            "Miércoles": "W",
            "Miercoles": "W",
            "Jueves": "H",
            "Viernes": "F",
            "Sábado": "A",
            "Sabado": "A",
            "Domingo": "S",
        }

        horario_format = horario

        # Reemplazar los días en la cadena de horario
        for dia, abreviatura in dias_mapeo.items():
            horario_format = horario_format.replace(dia, abreviatura).replace(", ", "")

        horario_format = f"acl {automation_name.replace(" ", "_")} time {horario_format.replace(' - ', '-').replace('  ', ' ')}"

        # Leer el contenido del archivo squid.conf
        with open("/etc/squid/squid.conf", "r") as archivo:
            lineas = archivo.readlines()

        indice_referencia = None
        for i, linea in enumerate(lineas):
            if "# Horario de restricciones" in linea:
                indice_referencia = i
                break

        if indice_referencia:
            lineas.insert(indice_referencia + 1, "\n")  # Inserta una línea en blanco
            lineas.insert(indice_referencia + 2, horario_format)

            with open("/etc/squid/squid.conf", "w") as archivo:
                archivo.writelines(lineas)

        # subprocess.run(["systemctl", "restart", "squid"])

        automation = Automation(
            0,
            automation_name,
            automation_type,
            restriccion,
            horario,
            1,
            fecha_creacion,
            comunidad_id,
            current_user.id,
        )
        automation = modelAutomation.insertAutomation(automation)

        return jsonify({"message": "Automatizacion creada correctamente!"})
    except subprocess.CalledProcessError:
        return jsonify({"error": "Error al permitir el puerto."})


# Ejecutara unicamente dominios que las ips sean dinamicas
def verify_domain_dynamic(domain):
    ips_set = set()  # Conjunto para almacenar las IPs únicas
    ips = []
    ips_sorted = None

    for _ in range(5):  # Ejecutar el comando cinco veces
        salida = subprocess.check_output(["/bin/dig", "+short", domain])
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

        return common_ip
    else:
        # Convertir el conjunto a una lista y ordenarla
        ips_sorted = sorted(list(ips_set))
        return ips_sorted


def allow_connections_detail(
    id_regla,
    regla_name,
    action_rule,
    entry,
    domain,
):
    try:
        saved_domains = []

        direction = "-s" if entry == "INPUT" else "-d"

        comment_domain = f"{regla_name} - {domain}"

        if domain in plataformas_dinamicas_dominio:
            ip_domain = verify_domain_dynamic(domain)

            if isinstance(ip_domain, list):
                rules_domain_dynamic = [
                    f"/sbin/iptables -I {entry} 1 {direction} {ip} -j {action_rule} -m comment --comment '{comment_domain}'"
                    for ip in ip_domain
                ]
            elif isinstance(ip_domain, str):
                rules_domain_dynamic = [
                    f"/sbin/iptables -I {entry} 1 {direction} {ip_domain} -j {action_rule} -m comment --comment '{comment_domain}'"
                ]
        else:
            rules_domain_dynamic = [
                f"/sbin/iptables -I {entry} 1 {direction} {domain} -j {action_rule} -m comment --comment '{comment_domain}'"
            ]

        rule_details = modelFirewallDetail.getRulesDetailsById(id_regla)

        for detail_rule in rule_details:
            detail_domain = (
                detail_rule[1].split(" -m comment --comment ")[1].replace("'", "")
            )

            count_hyphens = detail_domain.count("-")

            if count_hyphens == 2:
                processed_domain = detail_domain.split("-", 2)[2].strip()

            elif count_hyphens == 1:
                processed_domain = detail_domain.split("-", 1)[1].strip()

            if "www" in processed_domain:
                processed_domain_no_www = processed_domain.split("www.")[1]
                saved_domains.append(processed_domain_no_www)
            else:
                saved_domains.append(processed_domain)

        if "www" in domain:
            domain_no_www = domain.split("www.")[1]
        else:
            domain_no_www = domain

        if domain_no_www not in saved_domains:
            for rule in rules_domain_dynamic:
                subprocess.run(shlex.split(rule))

                firewall_detail = FirewallDetail(0, id_regla, rule, 1)
                modelFirewallDetail.insertRuleDetail(firewall_detail)
        else:
            return jsonify(
                {"error": "El dominio ya esta presente en este tipo de contenido"}
            )

        if action_rule == "REJECT":
            add_domain_to_hosts(domain, comment_domain)

        save_iptables_rules()

        return jsonify({"message": "¡Regla creada correctamente!"})
    except subprocess.CalledProcessError:
        return "Error al crear la regla."


def generate_content_domain(content, prefix):
    content_domain = f"{prefix}"
    content_domain_dynamic = ""
    plataforms_set = set()

    for platform in content:
        if platform in plataformas:
            domains = [f" {domain} or" for domain in plataformas[platform]]
            content_domain += "".join(domains)
            plataforms_set.add(platform)

        if platform in plataformas_dinamicas:
            for domainPlataform in plataformas_dinamicas[platform]:
                ip_domain = verify_domain_dynamic(domainPlataform)

                if isinstance(ip_domain, list):
                    for ip in ip_domain:
                        domains = f" {ip} or"
                        content_domain += "".join(domains)
                        plataforms_set.add(platform)

                elif isinstance(ip_domain, str):
                    content_domain_dynamic += f" {ip_domain} or"
                    plataforms_set.add(platform)

    plataforms = " - ".join(plataforms_set)

    content_domain = content_domain.rstrip(" or")
    plataforms = plataforms.rstrip(" -")
    content_domain_dynamic = content_domain_dynamic.rstrip(" or")

    return content_domain, plataforms, content_domain_dynamic


def process_content(content, domain_type):
    domain_content, platforms_content, dynamic_content = generate_content_domain(
        content, domain_type
    )
    content_filter = f"{domain_content}"
    platforms = f"{platforms_content}"

    if dynamic_content != "":
        content_filter = f"{content_filter} or {'dst net' if domain_type == 'dst host' else 'net'}{dynamic_content}"

    return content_filter, platforms


def process_domains(domains, prefix):
    domain_string_dynamic = ""
    domain_string_static = ""
    domain_list_dynamic = ""

    for domain in domains:
        domain_line = domain.strip()

        if domain_line in plataformas_dinamicas_dominio:
            ip_domain = verify_domain_dynamic(domain_line)

            if isinstance(ip_domain, list):
                domain_list_dynamic += " or ".join(ip_domain) + " or "
            elif isinstance(ip_domain, str):
                domain_string_dynamic += ip_domain + " or "
        else:
            domain_string_static += domain_line + " or "

    domain_list_dynamic = domain_list_dynamic.rstrip(" or ")
    domain_string_dynamic = domain_string_dynamic.rstrip(" or ")
    domain_string_static = domain_string_static.rstrip(" or ")

    # Generar el valor de general_domain
    if domain_string_dynamic and domain_string_static and domain_list_dynamic:
        general_domain = f"{prefix}host {domain_string_static} or {domain_list_dynamic} or {prefix}net {domain_string_dynamic}"
    elif domain_string_static and domain_list_dynamic:
        general_domain = f"{prefix}host {domain_string_static} or {domain_list_dynamic}"
    elif domain_string_dynamic and domain_string_static:
        general_domain = f"{prefix}host {domain_string_static} or {prefix}net {domain_string_dynamic}"
    elif domain_string_dynamic and domain_list_dynamic:
        general_domain = (
            f"{prefix}host {domain_list_dynamic} or {prefix}net {domain_string_dynamic}"
        )
    elif domain_string_static:
        general_domain = f"{prefix}host {domain_string_static}"
    elif domain_list_dynamic:
        general_domain = f"{prefix}host {domain_list_dynamic}"
    elif domain_string_dynamic:
        general_domain = f"{prefix}net {domain_string_dynamic}"

    return general_domain


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
    domain_dst,
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
            contents_filter, plataforms = process_content(content_dst, "dst host")
        elif generalContent:
            contents_filter, plataforms = process_content(generalContent, "host")

        if generalDomain or domain_dst:
            prefix = "dst " if domain_dst else ""

            domains = (
                generalDomain.split(",") if generalDomain else domain_dst.split(",")
            )
            general_domain = process_domains(domains, prefix)

            name_filter += " - " + (
                generalDomain if generalDomain else (domain_dst if domain_dst else "")
            )
            name_filter = name_filter.replace(",", ", ")

            ips_custom = general_domain.replace("/", "-")

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
            contents_filter = contents_filter.replace("/", "-")
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


def pre_start_capture():
    # Comando arp-scan para escanear la red
    command = "/sbin/arp-scan -l"
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    stdout, _ = process.communicate()

    # Decodificar la salida del comando arp-scan de bytes a texto
    output = stdout.decode()

    interface = (
        output.strip().split("\n")[0].split(",")[0].split("Interface:")[1].strip()
    )

    custom_command = (
        "(tcp or udp) and (port http or https or smtp or ssh or ftp or telnet)"
    )

    base_command = [
        "/sbin/tcpdump",
        # "-n"   # Muestra el trafico los host en formato de ip y no de dominio
        "-l",
        "-c",
        "80",
        "-i",
        interface,
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
        if packet_count >= 80:
            break

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

            yield f"data: {time_formatted} {src_ip_domain}:{src_port} > {dst_ip_domain}:{dst_port} {protocol} {info}\n\n"

    # Después de salir del bucle de captura, cerrar la conexión EventSource
    yield "event: close\n\n"


def start_capture(command_id, command_filter, count_packets):
    # Comando arp-scan para escanear la red
    command_networks = "/sbin/arp-scan -l"
    process_networks = subprocess.Popen(
        command_networks, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    stdout, _ = process_networks.communicate()

    # Decodificar la salida del comando arp-scan de bytes a texto
    output = stdout.decode()

    interface = (
        output.strip().split("\n")[0].split(",")[0].split("Interface:")[1].strip()
    )

    base_command = f"/bin/tcpdump -l -c {count_packets} -i {interface}"

    default_filter = (
        "(tcp or udp) and (port http or https or smtp or ssh or ftp or telnet)"
    )
    custom_command = (
        command_filter.replace("-", "/") if command_filter else default_filter
    )

    filterData = modelFilterPacket.getFiltersById(command_id)
    nombre_filtro = filterData[1]
    tipo_filtro = filterData[2]
    tipo_consumo = filterData[4]

    if "Dominio" in tipo_filtro:
        prefix = "dst " if "dst " in command_filter else ""

        if "-" in nombre_filtro:
            _, domain_filter = map(str.strip, nombre_filtro.split(" - "))

            domains = domain_filter.split(",")
            domain_command = process_domains(domains, prefix)

            domain_command = domain_command.replace("-", "/")

            custom_values = [
                domain_command,
            ]

    elif tipo_consumo:
        prefix = "dst " if "dst " in command_filter else ""

        consumos = tipo_consumo.split()

        if prefix:
            content_command, _ = process_content(consumos, "dst host")

        else:
            content_command, _ = process_content(consumos, "host")

        custom_values = content_command

    else:
        custom_values = custom_command

    end_command = "-tttt -q -v"

    # Concatenar las dos partes del comando
    command = f"{base_command} '{custom_values}' {end_command}"

    print("Comando > ", command)

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True,
        shell=True,
    )

    def generate():
        packet_count = 0

        for stdout_line in iter(process.stdout.readline, ""):
            if packet_count >= int(count_packets):
                break
            if "ARP" in stdout_line:
                arp_info = stdout_line.strip().split(",")
                arp_parts = arp_info[0].split(" ")
                time = " ".join(arp_parts[:2])
                time_formatted = datetime.strptime(
                    time, "%Y-%m-%d %H:%M:%S.%f"
                ).strftime("%Y-%m-%d %H:%M:%S")
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

                combined_line = stdout_line.strip() + " " + line2.strip()

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
                    time_formatted = datetime.strptime(
                        time, "%Y-%m-%d %H:%M:%S.%f"
                    ).strftime("%Y-%m-%d %H:%M:%S")

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

                    yield f"data: {time_formatted} {src_ip_domain}:{src_port} > {dst_ip_domain}:{dst_port} {protocol} {info}\n\n"

        # Después de salir del bucle de captura, cerrar la conexión EventSource
        yield "event: close\n\n"

        process.stdout.close()

        for stderr_line in iter(process.stderr.readline, ""):
            yield f"data: ERROR: {stderr_line}\n\n"

        process.stderr.close()

        process.wait()

    return Response(generate(), mimetype="text/event-stream")


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
            nombre_filtro, tipo_filtro, filtro_creado, contenido, fecha = filtro[1:6]
            name_domain = ""
            domain_filter = ""

            if "-" in nombre_filtro:
                name_domain, domain_filter = map(str.strip, nombre_filtro.split(" - "))

            ip, puerto, protocolo, protocolo_red = "", "", "", ""
            conjuntos_parentesis = re.findall(r"\((.*?)\)", filtro_creado)

            if contenido:
                consumo_formateado = (
                    contenido.title().replace("_", " ").replace("-", " ")
                )
            else:
                partes_con_palabras_clave, otras_partes = [], []

                if "Dominio" not in tipo_filtro:
                    for conjunto in conjuntos_parentesis:
                        if "host" in conjunto.lower():
                            ip = conjunto
                        elif "port" in conjunto.lower():
                            partes_puerto = re.split(r"\b(and|or)\b", conjunto.lower())

                            for parte in partes_puerto:
                                if parte not in ["and", "or"]:
                                    lista = (
                                        partes_con_palabras_clave
                                        if any(
                                            palabra in parte
                                            for palabra in palabras_clave
                                        )
                                        else otras_partes
                                    )
                                    lista.append(parte.strip())

                            protocolo_red = " ".join(partes_con_palabras_clave)
                            puerto = " ".join(otras_partes)
                        else:
                            protocolo = conjunto

                consumo_formateado = ""

            puerto = puerto.replace("port", "").replace("src", "").replace("dst", "")
            puertos = puerto.split()
            puerto = ", ".join(puertos)

            protocolo_red = (
                protocolo_red.replace("port", "").replace("src", "").replace("dst", "")
            )
            protocolos_red = protocolo_red.split()
            protocolo_red = ", ".join(protocolos_red)

            filtro_formateado = {
                "id": filtro[0],
                "nombre_filtro": name_domain.title()
                if name_domain
                else nombre_filtro.title(),
                "tipo_filtro": tipo_filtro,
                "filtro": filtro[3],
                "fecha_creacion": fecha.strftime("%d-%m-%Y"),
                "ip": (ip if not domain_filter else domain_filter)
                .replace("host", "")
                .replace("src", "")
                .replace("dst", "")
                .replace(" and ", ", ")
                .replace(" or ", ", "),
                "puerto": puerto,
                "protocolo_red": protocolo_red,
                "protocolo": protocolo.replace(" or ", ", "),
                "consumos": consumo_formateado,
            }
            filtros_formateados.append(filtro_formateado)

        return filtros_formateados
    except Exception as e:
        return f"Error al cargar el reporte: {str(e)}"


def load_comunnity():
    try:
        comunidades = modelCommunity.getCommunity()

        if comunidades:
            registros_modificados = []
            for comunidad in comunidades:
                registro_modificado = list(comunidad)
                registro_modificado[2] = (
                    registro_modificado[2].replace("_", " ").title()
                )
                registro_modificado[4] = registro_modificado[4].strftime("%d-%m-%Y")
                registros_modificados.append(tuple(registro_modificado))

            return registros_modificados

        else:
            return comunidades
    except Exception as e:
        return f"Error al cargar el reporte: {str(e)}"
    
    
def load_automation():
    try:
        automatizaciones =  modelAutomation.getAutomation()

        if automatizaciones:
            print(automatizaciones)
            registros_modificados = []
            for comunidad in automatizaciones:
                registro_modificado = list(comunidad)
                registro_modificado[2] = (
                    registro_modificado[2].replace("_", " ").title()
                )
                registro_modificado[4] = registro_modificado[4].strftime("%d-%m-%Y")
                registros_modificados.append(tuple(registro_modificado))

            return registros_modificados

        else:
            return automatizaciones
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
        modelPaquetes.deletePacket(id_reporte)

        return "Reporte Eliminado"
    except subprocess.CalledProcessError as e:
        return f"Error al obtener el número de la regla: {e}"


def delete_filter(id_filter):
    try:
        modelFilterPacket.deleteFilter(id_filter)

        return "Reporte Eliminado"
    except Exception as e:
        return f"Error al obtener el número de la regla: {str(e)}"


def delete_community(id_community):
    try:
        modelCommunity.deleteCommunity(id_community)

        return "Comindad Eliminada"
    except Exception as e:
        return f"Error al obtener el número de la regla: {str(e)}"
