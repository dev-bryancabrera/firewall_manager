import sys
import logging
from models.funciones import (
    refresh_rule,
)

# Configuración del logger (opcional)
logging.basicConfig(
    filename="/var/log/call_refresh_rule.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def main():
    try:
        result = refresh_rule()
        logging.info(f"refresh_rule ejecutado con éxito. Resultado: {result}")
    except Exception as e:
        logging.error(f"Error al ejecutar refresh_rule: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
