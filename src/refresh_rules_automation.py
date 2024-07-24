import glob
import os
import re
import subprocess
import shlex
import logging
import sys

# Configuración del logger
logging.basicConfig(
    filename="/var/log/refresh_rule.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Crear un logger específico para refresh_rule
refresh_rule_logger = logging.getLogger("refresh_rule")

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


def refresh_rule():
    directory_path = "/etc/iptables-rules/automations/"
    rules = []

    # Obtener todos los archivos en el directorio especificado
    file_paths = glob.glob(os.path.join(directory_path, "*"))

    # Procesar cada archivo en el directorio
    for file_path in file_paths:
        if os.path.exists(file_path):
            try:
                # Limpiar las reglas de iptables FORWARD
                subprocess.check_output(["/sbin/iptables", "-F", "FORWARD"])
                refresh_rule_logger.info(
                    "Todas las reglas FORWARD han sido eliminadas correctamente."
                )
            except subprocess.CalledProcessError as e:
                refresh_rule_logger.error(f"Error al eliminar las reglas FORWARD: {e}")

            try:
                # Leer las reglas del archivo
                with open(file_path, "r") as rules_file:
                    lines = rules_file.readlines()
                    for line in lines:
                        # Extraer las partes usando expresiones regulares
                        match = re.match(
                            r"1:\s*(.*?)\s*2:\s*(.*?)\s*3:\s*(.*?)\s*4:\s*(.*)",
                            line.strip(),
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
                            refresh_rule_logger.info(f"Procesando regla: {rule}")

                            source = (
                                "" if source == "Todos los dispositivos" else source
                            )

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
                                    refresh_rule_logger.info(
                                        f"Regla ejecutada correctamente: {rule}"
                                    )
                                except subprocess.CalledProcessError as e:
                                    refresh_rule_logger.error(
                                        f"Error al ejecutar la regla: {rule} - {e}"
                                    )
            except Exception as e:
                refresh_rule_logger.error(
                    f"Error al procesar el archivo {file_path}: {e}"
                )


def main():
    try:
        result = refresh_rule()
        refresh_rule_logger.info(
            f"refresh_rule ejecutado con éxito. Resultado: {result}"
        )
    except Exception as e:
        refresh_rule_logger.error(f"Error al ejecutar refresh_rule: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
