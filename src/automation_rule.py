import re
import shlex
import sys
import logging
import subprocess
from datetime import datetime
import os

# Configuración del logging para automation_rule
automation_rule_logger = logging.getLogger("automation_rule")
automation_rule_logger.setLevel(logging.INFO)

# Configura un handler para escribir en un archivo
file_handler = logging.FileHandler("/var/log/automation_rule.log")
file_handler.setLevel(logging.INFO)  # Ajusta el nivel de logging para el archivo
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

automation_rule_logger.addHandler(file_handler)

# Configuración del logger principal
logging.basicConfig(
    filename="/var/log/call_automation_rule.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

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


def deactivate_domain_iptables_list(name_domain):
    file_path = "/etc/iptables-rules/rules-list"

    with open(file_path, "r") as list_file:
        lines = list_file.readlines()

    with open(file_path, "w") as list_file:
        for line in lines:
            if name_domain.lower() in line.lower() and not line.strip().startswith("#"):
                list_file.write(f"#{line}")
            else:
                list_file.write(line)


def activate_domain_iptables_list(name_domain, file_path):
    with open(file_path, "r") as list_file:
        lines = list_file.readlines()

    with open(file_path, "w") as list_file:
        for line in lines:
            if name_domain in line and line.strip().startswith("#"):
                list_file.write(line.lstrip("#"))
            else:
                list_file.write(line)


def automation_rule(automation_script):
    file_path = f"/etc/iptables-rules/automations/{automation_script}"

    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                primera_linea = file.readline().strip()

                # Extraer el nombre de la regla de la primera línea
                match = re.search(r"Nombre de la Regla: (.+)", primera_linea)
                if match:
                    nombre_regla = match.group(1)
                    deactivate_domain_iptables_list(nombre_regla)
                    activate_domain_iptables_list(nombre_regla, file_path)
                else:
                    automation_rule_logger.warning(
                        "No se encontró el nombre de la regla en la primera línea."
                    )

                file.readline()

                # Leer y procesar desde la tercera línea
                rules = []
                for line in file:
                    line = line.strip()
                    # Extraer las partes usando expresiones regulares
                    match = re.match(
                        r"1:\s*(.*?)\s*2:\s*(.*?)\s*3:\s*(.*?)\s*4:\s*(.*)", line
                    )

                    if match:
                        source = match.group(1).strip()
                        domain = match.group(2).strip()
                        action = match.group(3).strip()
                        comment = match.group(4).strip()

                        rule = {
                            "source": source,
                            "domain": domain,
                            "action": action,
                            "comment": comment,
                        }
                        rules.append(rule)

                        automation_rule_logger.info(f"Procesando regla: {rule}")

                        source = "" if source == "Todos los dispositivos" else source

                        if domain in plataformas_dinamicas_dominio:
                            ip_domain = verify_domain_dynamic(domain)
                            if isinstance(ip_domain, list):
                                rules_domain_dynamic = [
                                    f"/sbin/iptables -I FORWARD 1 {source} -d {ip} -j {action} -m comment --comment '{comment}'"
                                    for ip in ip_domain
                                ]
                            elif isinstance(ip_domain, str):
                                rules_domain_dynamic = [
                                    f"/sbin/iptables -I FORWARD 1 {source} -d {ip_domain} -j {action} -m comment --comment '{comment}'"
                                ]
                        else:
                            rules_domain_dynamic = [
                                f"/sbin/iptables -I FORWARD 1 {source} -d {domain} -j {action} -m comment --comment '{comment}'"
                            ]

                        for rule in rules_domain_dynamic:
                            try:
                                subprocess.run(shlex.split(rule), check=True)
                                automation_rule_logger.info(
                                    f"Regla ejecutada correctamente: {rule}"
                                )
                            except subprocess.CalledProcessError as e:
                                automation_rule_logger.error(
                                    f"Error al ejecutar la regla: {rule} - {e}"
                                )

        except Exception as e:
            automation_rule_logger.error(f"Error al procesar el archivo: {e}")
    else:
        automation_rule_logger.warning(f"El archivo {file_path} no existe.")


def obtener_automatizacion_actual():
    try:
        logging.info("Iniciando obtención de la automatización actual.")

        # Obtener el contenido actual del crontab
        resultado = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True, check=True
        )
        crontab_actual = resultado.stdout
        logging.info("Contenido del crontab obtenido correctamente.")

        # Obtener la hora actual
        ahora = datetime.now()
        minuto_actual = ahora.minute
        hora_actual = ahora.hour
        dia_actual = ahora.weekday() + 1

        # Convertir dia_actual a formato cron
        dia_actual_cron = str(dia_actual)

        logging.info(
            f"Hora actual: {hora_actual}, Minuto actual: {minuto_actual}, Día actual: {dia_actual_cron}"
        )

        comentario = ""
        # Analizar cada línea del crontab
        for linea in crontab_actual.split("\n"):
            logging.debug(f"Procesando línea: {linea}")
            if linea.startswith("# Automatización"):
                comentario = linea
                logging.debug(f"Comentario encontrado: {comentario}")
            else:
                match = re.match(r"(\d+)\s+(\d+)\s+\*\s+\*\s+([\d,]+)\s+(.+)", linea)
                if match:
                    minutos = int(match.group(1))
                    horas = int(match.group(2))
                    dias = match.group(3).split(
                        ","
                    )  # Dividir por comas para manejar múltiples días
                    comando = match.group(4)

                    logging.debug(
                        f"Minutos: {minutos}, Horas: {horas}, Días: {dias}, Comando: {comando}"
                    )

                    if (
                        minutos == minuto_actual
                        and horas == hora_actual
                        and dia_actual_cron in dias
                    ):
                        # Extraer el nombre de la automatización del comentario anterior
                        nombre_automatizacion = re.search(
                            r"# Automatización (.+) - ", comentario
                        ).group(1)
                        logging.info(
                            f"Nombre de la automatización encontrado: {nombre_automatizacion}"
                        )
                        return nombre_automatizacion

        logging.info("No se encontró ninguna automatización coincidente.")
        return None
    except Exception as e:
        logging.error(f"Error al obtener la automatización actual: {e}")
        return None


def main():
    try:
        nombre_automatizacion = obtener_automatizacion_actual()
        if nombre_automatizacion:
            automation_rule(nombre_automatizacion)
            logging.info(
                f"automation_rule ejecutado con éxito para: {nombre_automatizacion}"
            )
        else:
            logging.warning(
                f"No se pudo determinar la automatización actual.{nombre_automatizacion}"
            )
    except Exception as e:
        logging.error(f"Error al ejecutar automation_rule: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
