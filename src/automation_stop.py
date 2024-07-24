import re
import shlex
import sys
import logging
import subprocess
from datetime import datetime
import os

# Configuración del logging para stop_automation_rule
stop_automation_rule_logger = logging.getLogger("stop_automation_rule")
stop_automation_rule_logger.setLevel(logging.INFO)

# Configura un handler para escribir en un archivo
file_handler = logging.FileHandler("/var/log/stop_automation_rule.log")
file_handler.setLevel(logging.INFO)  # Ajusta el nivel de logging para el archivo
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

stop_automation_rule_logger.addHandler(file_handler)

# Configuración del logger principal
logging.basicConfig(
    filename="/var/log/call_stop_automation_rule.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def deactivate_domain_iptables_list(name_domain, file_path):
    with open(file_path, "r") as list_file:
        lines = list_file.readlines()

    with open(file_path, "w") as list_file:
        for line in lines:
            if name_domain in line and not line.strip().startswith("#"):
                list_file.write(f"#{line}")
            else:
                list_file.write(line)


def iptables_rules_matched(name_iptable):
    salida_iptables = subprocess.check_output(
        ["/sbin/iptables", "-L", "FORWARD", "--line-numbers", "-n"]
    )

    reglas = salida_iptables.decode("utf-8").splitlines()
    id_iptable_delete = None

    consulta_formateada = "\n".join(reglas[2:])

    for line in consulta_formateada.splitlines():
        id_iptable_rule = line.split()[0]
        if name_iptable.lower() in line.lower():
            if id_iptable_delete is None:
                id_iptable_delete = id_iptable_rule

            rule_delete = f"/sbin/iptables -D FORWARD {id_iptable_delete}"

            subprocess.run(
                shlex.split(f"{rule_delete}"),
            )

    return "¡Regla Eliminada Correctamente!"


def stop_automation_rule(automation_script):
    file_path = f"/etc/iptables-rules/automations/{automation_script}"

    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                primera_linea = file.readline().strip()

            # Extraer el nombre de la regla de la primera línea
            match = re.search(r"Nombre de la Regla: (.+)", primera_linea)
            if match:
                nombre_regla = match.group(1)
                deactivate_domain_iptables_list(nombre_regla, file_path)
                iptables_rules_matched(nombre_regla)
            else:
                stop_automation_rule_logger.warning(
                    "No se encontró el nombre de la regla en la primera línea."
                )

            stop_automation_rule_logger.info(
                "Todas las reglas FORWARD han sido eliminadas correctamente."
            )

        except Exception as e:
            stop_automation_rule_logger.error(f"Error al procesar el archivo: {e}")
    else:
        stop_automation_rule_logger.warning(f"El archivo {file_path} no existe.")


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
            stop_automation_rule(nombre_automatizacion)
            logging.info(
                f"stop_automation_rule ejecutado con éxito para: {nombre_automatizacion}"
            )
        else:
            logging.warning(
                f"No se pudo determinar la automatización actual.{nombre_automatizacion}"
            )
    except Exception as e:
        logging.error(f"Error al ejecutar stop_automation_rule: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
