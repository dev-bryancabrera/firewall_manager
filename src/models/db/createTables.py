from .connectDB import get_connection


class createTable:
    @classmethod
    def createTables(self):
        db = None
        try:
            db = get_connection()
            cursor = db.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS filtro_monitoreo (id INT AUTO_INCREMENT PRIMARY KEY, nombre_filtro TEXT, tipo_filtro VARCHAR(255), filtro TEXT, contenido TEXT, fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, user_id INT, FOREIGN KEY (user_id) REFERENCES user(id))"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS firewall_rules (id INT AUTO_INCREMENT PRIMARY KEY, nombre_regla TEXT, tipo_regla TEXT, fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, estado BOOLEAN, user_id INT, FOREIGN KEY (user_id) REFERENCES user(id))"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS firewall_rules_detail (id INT AUTO_INCREMENT PRIMARY KEY, regla VARCHAR(255), estado BOOLEAN, firewall_rule_id INT, FOREIGN KEY (firewall_rule_id) REFERENCES firewall_rules(id))"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS monitoreo_reporte (id INT AUTO_INCREMENT PRIMARY KEY, nombre_reporte VARCHAR(255), reporte LONGBLOB, fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, filtro_monitoreo TEXT, user_id INT, FOREIGN KEY (user_id) REFERENCES user(id))"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS comunidades (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(255), tipo VARCHAR(80), rango TEXT, fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, estado TINYINT(1) DEFAULT 1, user_id INT, FOREIGN KEY (user_id) REFERENCES user(id))"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS automatizacion_firewall (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(255), tipo VARCHAR(80), restriccion TEXT, restriccion_proxy TEXT, horario TEXT, estado TINYINT(1) DEFAULT 1, fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, comunidad_id INT, user_id INT, FOREIGN KEY (comunidad_id) REFERENCES comunidades(id), FOREIGN KEY (user_id) REFERENCES user(id))"
            )
            db.commit()
            cursor.close()
            db.close()
            return "Base de datos y tablas creadas correctamente"
        except Exception as ex:
            db.rollback()
            raise Exception(ex)
